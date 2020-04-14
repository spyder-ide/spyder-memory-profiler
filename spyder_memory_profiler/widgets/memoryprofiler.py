# -*- coding: utf-8 -*-
#
# Copyright © 2011 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Memory Profiler widget

See the official documentation of memory_profiler:
https://pypi.python.org/pypi/memory_profiler/
"""

# Standar library imports
from __future__ import with_statement
import hashlib
import inspect
import linecache
import os
import os.path as osp
import sys
import time

# Third party imports
from qtpy.compat import getopenfilename
from qtpy.QtCore import (QByteArray, QProcess, Qt, QTextCodec,
                         QProcessEnvironment, Signal)
from qtpy.QtGui import QBrush, QColor, QFont
from qtpy.QtWidgets import (QHBoxLayout, QWidget, QMessageBox, QVBoxLayout,
                            QLabel, QTreeWidget, QTreeWidgetItem, QApplication)
from spyder.config.base import get_conf_path, get_translation
from spyder.plugins.variableexplorer.widgets.texteditor import TextEditor
from spyder.utils import programs
from spyder.utils.misc import add_pathlist_to_PYTHONPATH, get_python_executable
from spyder.utils.qthelpers import create_toolbutton, get_icon
from spyder.widgets.comboboxes import PythonModulesComboBox

try:
    from spyder.py3compat import to_text_string, getcwd
except ImportError:
    # python2
    to_text_string = unicode
    getcwd = os.getcwdu


locale_codec = QTextCodec.codecForLocale()
_ = get_translation("memory_profiler", dirname="spyder_memory_profiler")

COL_NO = 0
COL_USAGE = 1
COL_INCREMENT = 2
COL_LINE = 3
COL_POS = 0  # Position is not displayed but set as Qt.UserRole

CODE_NOT_RUN_COLOR = QBrush(QColor.fromRgb(128, 128, 128, 200))

WEBSITE_URL = 'https://pypi.python.org/pypi/memory_profiler/'


def is_memoryprofiler_installed():
    """
    Checks if the library for memory_profiler is installed.
    """
    return programs.is_module_installed('memory_profiler')


class MemoryProfilerWidget(QWidget):
    """
    Memory profiler widget.
    """
    DATAPATH = get_conf_path('memoryprofiler.results')
    VERSION = '0.0.1'
    redirect_stdio = Signal(bool)
    sig_finished = Signal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        # Need running QApplication before importing runconfig
        from spyder.preferences import runconfig
        self.runconfig = runconfig
        self.spyder_pythonpath = None

        self.setWindowTitle("Memory profiler")

        self.output = None
        self.error_output = None

        self.use_colors = True

        self._last_wdir = None
        self._last_args = None
        self._last_pythonpath = None

        self.filecombo = PythonModulesComboBox(self)

        self.start_button = create_toolbutton(
            self, icon=get_icon('run.png'),
            text=_("Profile memory usage"),
            tip=_("Run memory profiler"),
            triggered=(lambda checked=False: self.analyze()),
            text_beside_icon=True)
        self.stop_button = create_toolbutton(
            self,
            icon=get_icon('terminate.png'),
            text=_("Stop"),
            tip=_("Stop current profiling"),
            text_beside_icon=True)
        self.filecombo.valid.connect(self.start_button.setEnabled)
        #self.connect(self.filecombo, SIGNAL('valid(bool)'), self.show_data)
        # FIXME: The combobox emits this signal on almost any event
        #        triggering show_data() too early, too often.

        browse_button = create_toolbutton(
            self, icon=get_icon('fileopen.png'),
            tip=_('Select Python script'),
            triggered=self.select_file)

        self.datelabel = QLabel()

        self.log_button = create_toolbutton(
            self, icon=get_icon('log.png'),
            text=_("Output"),
            text_beside_icon=True,
            tip=_("Show program's output"),
            triggered=self.show_log)

        self.datatree = MemoryProfilerDataTree(self)

        self.collapse_button = create_toolbutton(
            self,
            icon=get_icon('collapse.png'),
            triggered=lambda dD=-1: self.datatree.collapseAll(),
            tip=_('Collapse all'))
        self.expand_button = create_toolbutton(
            self,
            icon=get_icon('expand.png'),
            triggered=lambda dD=1: self.datatree.expandAll(),
            tip=_('Expand all'))

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.filecombo)
        hlayout1.addWidget(browse_button)
        hlayout1.addWidget(self.start_button)
        hlayout1.addWidget(self.stop_button)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.collapse_button)
        hlayout2.addWidget(self.expand_button)
        hlayout2.addStretch()
        hlayout2.addWidget(self.datelabel)
        hlayout2.addStretch()
        hlayout2.addWidget(self.log_button)

        layout = QVBoxLayout()
        layout.addLayout(hlayout1)
        layout.addLayout(hlayout2)
        layout.addWidget(self.datatree)
        self.setLayout(layout)

        self.process = None
        self.set_running_state(False)
        self.start_button.setEnabled(False)

        if not is_memoryprofiler_installed():
            for widget in (self.datatree, self.filecombo, self.log_button,
                           self.start_button, self.stop_button, browse_button,
                           self.collapse_button, self.expand_button):
                widget.setDisabled(True)
            text = _(
                '<b>Please install the <a href="%s">memory_profiler module</a></b>'
                ) % WEBSITE_URL
            self.datelabel.setText(text)
            self.datelabel.setOpenExternalLinks(True)
        else:
            pass  # self.show_data()

    def analyze(self, filename=None, wdir=None, args=None, pythonpath=None,
                use_colors=True):
        self.use_colors = use_colors
        if not is_memoryprofiler_installed():
            return
        self.kill_if_running()
        # FIXME: storing data is not implemented yet
        if filename is not None:
            filename = osp.abspath(to_text_string(filename))
            index = self.filecombo.findText(filename)
            if index == -1:
                self.filecombo.addItem(filename)
                self.filecombo.setCurrentIndex(self.filecombo.count()-1)
            else:
                self.filecombo.setCurrentIndex(index)
            self.filecombo.selected()
        if self.filecombo.is_valid():
            filename = to_text_string(self.filecombo.currentText())
            runconf = self.runconfig.get_run_configuration(filename)
            if runconf is not None:
                if wdir is None:
                    if runconf.wdir_enabled:
                        wdir = runconf.wdir
                    elif runconf.cw_dir:
                        wdir = os.getcwd()
                    elif runconf.file_dir:
                        wdir = osp.dirname(filename)
                    elif runconf.fixed_dir:
                        wdir = runconf.dir
                if args is None:
                    if runconf.args_enabled:
                        args = runconf.args
            if wdir is None:
                wdir = osp.dirname(filename)
            if pythonpath is None:
                pythonpath = self.spyder_pythonpath
            self.start(wdir, args, pythonpath)

    def select_file(self):
        self.redirect_stdio.emit(False)
        filename, _selfilter = getopenfilename(
            self, _("Select Python script"), getcwd(),
            _("Python scripts")+" (*.py ; *.pyw)")
        self.redirect_stdio.emit(False)
        if filename:
            self.analyze(filename)

    def show_log(self):
        if self.output:
            editor = TextEditor(self.output, title=_("Memory profiler output"),
                                readonly=True)
            # Call .show() to dynamically resize editor;
            # see spyder-ide/spyder#12202
            editor.show()
            editor.exec_()

    def show_errorlog(self):
        if self.error_output:
            editor = TextEditor(self.error_output,
                                title=_("Memory profiler output"),
                                readonly=True)
            # Call .show() to dynamically resize editor;
            # see spyder-ide/spyder#12202
            editor.show()
            editor.exec_()

    def start(self, wdir=None, args=None, pythonpath=None):
        filename = to_text_string(self.filecombo.currentText())
        if wdir is None:
            wdir = self._last_wdir
            if wdir is None:
                wdir = osp.basename(filename)
        if args is None:
            args = self._last_args
            if args is None:
                args = []
        if pythonpath is None:
            pythonpath = self._last_pythonpath
        self._last_wdir = wdir
        self._last_args = args
        self._last_pythonpath = pythonpath

        self.datelabel.setText(_('Profiling, please wait...'))

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        self.process.setWorkingDirectory(wdir)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(
            lambda: self.read_output(error=True))
        self.process.finished.connect(self.finished)
        self.stop_button.clicked.connect(self.process.kill)

        if pythonpath is not None:
            env = [to_text_string(_pth)
                   for _pth in self.process.systemEnvironment()]
            add_pathlist_to_PYTHONPATH(env, pythonpath)
            processEnvironment = QProcessEnvironment()
            for envItem in env:
                envName, separator, envValue = envItem.partition('=')
                processEnvironment.insert(envName, envValue)
            self.process.setProcessEnvironment(processEnvironment)

        self.output = ''
        self.error_output = ''

        # remove previous results, since memory_profiler appends to output file
        # instead of replacing
        if osp.isfile(self.DATAPATH):
            os.remove(self.DATAPATH)

        if os.name == 'nt':
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            filename = osp.normpath(filename).replace(os.sep, '/')
            p_args = ['-m', 'memory_profiler', '-o', '"' + self.DATAPATH + '"',
                      '"' + filename + '"']
            if args:
                p_args.extend(programs.shell_split(args))
            executable = get_python_executable()
            executable += ' ' + ' '.join(p_args)
            executable = executable.replace(os.sep, '/')
            self.process.start(executable)
        else:
            p_args = ['-m', 'memory_profiler', '-o', self.DATAPATH, filename]
            if args:
                p_args.extend(programs.shell_split(args))
            executable = get_python_executable()
            self.process.start(executable, p_args)

        running = self.process.waitForStarted()
        self.set_running_state(running)
        if not running:
            QMessageBox.critical(self, _("Error"),
                                 _("Process failed to start"))

    def set_running_state(self, state=True):
        self.start_button.setEnabled(not state)
        self.stop_button.setEnabled(state)

    def read_output(self, error=False):
        if error:
            self.process.setReadChannel(QProcess.StandardError)
        else:
            self.process.setReadChannel(QProcess.StandardOutput)
        qba = QByteArray()
        while self.process.bytesAvailable():
            if error:
                qba += self.process.readAllStandardError()
            else:
                qba += self.process.readAllStandardOutput()
        text = to_text_string(locale_codec.toUnicode(qba.data()))
        if error:
            self.error_output += text
        else:
            self.output += text

    def finished(self):
        self.set_running_state(False)
        self.show_errorlog()  # If errors occurred, show them.
        self.output = self.error_output + self.output
        # FIXME: figure out if show_data should be called here or
        #        as a signal from the combobox
        self.show_data(justanalyzed=True)
        self.sig_finished.emit()

    def kill_if_running(self):
        if self.process is not None:
            if self.process.state() == QProcess.Running:
                self.process.kill()
                self.process.waitForFinished()

    def show_data(self, justanalyzed=False):
        if not justanalyzed:
            self.output = None
        self.log_button.setEnabled(
            self.output is not None and len(self.output) > 0)
        self.kill_if_running()
        filename = to_text_string(self.filecombo.currentText())
        if not filename:
            return

        self.datatree.load_data(self.DATAPATH)
        self.datelabel.setText(_('Sorting data, please wait...'))
        QApplication.processEvents()
        self.datatree.show_tree()

        text_style = "<span style=\'color: #444444\'><b>%s </b></span>"
        date_text = text_style % time.strftime("%d %b %Y %H:%M",
                                               time.localtime())
        self.datelabel.setText(date_text)


class MemoryProfilerDataTree(QTreeWidget):
    """
    Convenience tree widget (with built-in model)
    to store and view memory profiler data.
    """
    edit_goto = Signal(str, int, str)

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.header_list = [
            _('Line #'), _('Memory usage'), _('Increment'), _('Line contents')]
        self.stats = None      # To be filled by self.load_data()
        self.max_time = 0      # To be filled by self.load_data()
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setColumnCount(len(self.header_list))
        self.setHeaderLabels(self.header_list)
        self.clear()
        self.itemActivated.connect(self.item_activated)

    def show_tree(self):
        """Populate the tree with memory profiler data and display it."""
        self.clear()  # Clear before re-populating
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        self.populate_tree()
        self.expandAll()
        for col in range(self.columnCount()-1):
            self.resizeColumnToContents(col)
        self.collapseAll()
        self.setSortingEnabled(True)
        self.sortItems(COL_POS, Qt.AscendingOrder)

    def load_data(self, profdatafile):
        """Load memory profiler data saved by memory_profiler module"""

        # NOTE: Description of lstats below is for line_profiler. Here we
        # create a mock Lstats class to emulate this behaviour, so we can reuse
        # the spyder_line_profiler code. The structure of lstats is the same,
        # but the entries (line_no, hits, total_time) are replaced
        # by (line_no, usage, increment)

        # lstats has the following layout :
        # lstats.timings =
        #     {(filename1, line_no1, function_name1):
        #         [(line_no1, hits1, total_time1),
        #          (line_no2, hits2, total_time2)],
        #      (filename2, line_no2, function_name2):
        #         [(line_no1, hits1, total_time1),
        #          (line_no2, hits2, total_time2),
        #          (line_no3, hits3, total_time3)]}
        # lstats.unit = time_factor

        with open(profdatafile, 'r') as fid:
            reslines = fid.readlines()

        # get the results into an "lstats"-like format so that the code below
        # (originally for line_profiler) can be used without much modification
        class Lstats(object):
            def __init__(self):
                self.timings = {}
        lstats = Lstats()
        # find lines in results where new function starts
        newFuncAtLine = []
        for i, line in enumerate(reslines):
            if line.startswith('Filename: '):
                newFuncAtLine.append(i)
        # parse results from each function
        for i in newFuncAtLine:
            # filename
            filename = reslines[i].rstrip()[10:]
            # line number
            l = reslines[i+4].lstrip()
            line_no = int(l[:l.find(' ')])
            # function name
            l = reslines[i+5]
            function_name = l[l.find('def')+4:l.find('(')]
            # initiate structure
            lstats.timings[(filename, line_no, function_name)] = []
            # parse lines, add code lines and memory usage of current function
            for l in reslines[i+4:]:
                l = l.lstrip()
                # break on empty line (we have ended the current function results)
                if l == '':
                    break
                # split string (discard empty strings using filter)
                stuff = list(filter(None, l.split(' ')))
                # get line number, mem usage, and mem increment
                lineno = int(stuff[0])
                if len(stuff) >= 5 and stuff[2] == 'MiB':
                    usage = float(stuff[1])
                else:
                    usage = None
                if len(stuff) >= 5 and stuff[4] == 'MiB':
                    increment = float(stuff[3])
                else:
                    increment = None
                # append
                lstats.timings[(filename, line_no, function_name)].append(
                    (lineno, usage, increment))


        # First pass to group by filename
        self.stats = dict()
        linecache.checkcache()
        for func_info, stats in lstats.timings.items():
            # func_info is a tuple containing (filename, line, function anme)
            filename, start_line_no = func_info[:2]

            # Read code
            start_line_no -= 1  # include the @profile decorator
            all_lines = linecache.getlines(filename)
            block_lines = inspect.getblock(all_lines[start_line_no:])

            # Loop on each line of code
            func_stats = []
            func_initial_usage = stats[0][1]
            func_peak_usage = 0.0
            next_stat_line = 0
            for line_no, code_line in enumerate(block_lines):
                line_no += start_line_no + 1 # Lines start at 1
                code_line = code_line.rstrip('\n')
                if (next_stat_line >= len(stats)
                        or line_no != stats[next_stat_line][0]):
                    # Line didn't run
                    usage, increment = None, None
                else:
                    # Compute line stats
                    usage, increment = stats[next_stat_line][1:]
                    if usage is not None:
                        func_peak_usage = max(func_peak_usage, usage-func_initial_usage)
                    next_stat_line += 1
                func_stats.append(
                    [line_no, code_line, usage, increment])

            # Fill dict
            self.stats[func_info] = [func_stats, func_peak_usage]

    def fill_item(self, item, filename, line_no, code, usage, increment):
        item.setData(COL_POS, Qt.UserRole, (osp.normpath(filename), line_no))

        item.setData(COL_NO, Qt.DisplayRole, line_no)

        item.setData(COL_LINE, Qt.DisplayRole, code)

        if usage is None:
            usage = ''
        else:
            usage = '%.3f MiB' % (usage)
        item.setData(COL_USAGE, Qt.DisplayRole, usage)
        item.setTextAlignment(COL_USAGE, Qt.AlignCenter)

        if increment is None:
            increment = ''
        else:
            increment = '%.3f MiB' % (increment)
        item.setData(COL_INCREMENT, Qt.DisplayRole, increment)
        item.setTextAlignment(COL_INCREMENT, Qt.AlignCenter)

    def populate_tree(self):
        """Create each item (and associated data) in the tree"""
        if not self.stats:
            warn_item = QTreeWidgetItem(self)
            warn_item.setData(
                0, Qt.DisplayRole,
                _('No timings to display. '
                  'Did you forget to add @profile decorators ?')
                .format(url=WEBSITE_URL))
            warn_item.setFirstColumnSpanned(True)
            warn_item.setTextAlignment(0, Qt.AlignCenter)
            font = warn_item.font(0)
            font.setStyle(QFont.StyleItalic)
            warn_item.setFont(0, font)
            return

        try:
            monospace_font = self.window().editor.get_plugin_font()
        except AttributeError:  # If run standalone for testing
            monospace_font = QFont("Courier New")
            monospace_font.setPointSize(10)

        for func_info, func_data in self.stats.items():
            # Function name and position
            filename, start_line_no, func_name = func_info
            func_stats, func_peak_usage = func_data
            func_item = QTreeWidgetItem(self)
            func_item.setData(
                0, Qt.DisplayRole,
                _('{func_name} (peak {peak_usage:.3f} MiB) in file "{filename}", '
                  'line {line_no}').format(
                    filename=filename,
                    line_no=start_line_no,
                    func_name=func_name,
                    peak_usage=func_peak_usage))
            func_item.setFirstColumnSpanned(True)
            func_item.setData(COL_POS, Qt.UserRole,
                              (osp.normpath(filename), start_line_no))

            # For sorting by time
            func_item.setData(COL_USAGE, Qt.DisplayRole, func_peak_usage)
            func_item.setData(COL_INCREMENT, Qt.DisplayRole,
                              func_peak_usage)

            if self.parent().use_colors:
                # Choose deteministic unique color for the function
                md5 = hashlib.md5((filename + func_name).encode("utf8")).hexdigest()
                hue = (int(md5[:2], 16) - 68) % 360  # avoid blue (unreadable)
                func_color = QColor.fromHsv(hue, 200, 255)
            else:
                # Red color only
                func_color = QColor.fromRgb(255, 0, 0)

            # get max increment
            max_increment = 0
            for line_info in func_stats:
                (line_no, code_line, usage, increment) = line_info
                if increment is not None:
                    max_increment = max(max_increment, increment)

            # Lines of code
            for line_info in func_stats:
                line_item = QTreeWidgetItem(func_item)
                (line_no, code_line, usage, increment) = line_info
                self.fill_item(
                    line_item, filename, line_no, code_line,
                    usage, increment)

                # Color background
                if increment is not None:
                    if increment > 0 and max_increment > 0:
                        alpha = increment / max_increment
                    else:
                        alpha = 0
                    color = QColor(func_color)
                    color.setAlphaF(alpha)  # Returns None
                    color = QBrush(color)
                    for col in range(self.columnCount()):
                        line_item.setBackground(col, color)
                else:

                    for col in range(self.columnCount()):
                        line_item.setForeground(col, CODE_NOT_RUN_COLOR)

                # Monospace font for code
                line_item.setFont(COL_LINE, monospace_font)

    def item_activated(self, item):
        filename, line_no = item.data(COL_POS, Qt.UserRole)
        self.edit_goto.emit(filename, line_no, '')


def test():
    """Run widget test"""
    from spyder.utils.qthelpers import qapplication
    app = qapplication()
    widget = MemoryProfilerWidget(None)
    widget.resize(800, 600)
    widget.show()
    widget.analyze(osp.normpath(osp.join(osp.dirname(__file__), os.pardir,
                                         'tests/profiling_test_script.py')),
                   use_colors=True)
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
