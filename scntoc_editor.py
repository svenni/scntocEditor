from PyQt4 import QtCore, QtGui

import scntoc
import os
import sys

MODEL_ROLE = QtCore.Qt.UserRole
RES_ROLE = MODEL_ROLE + 1

from xml.dom import minidom
import xml.etree.ElementTree as ET


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'ISO-8859-1')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class ScntocEditor(QtGui.QDialog):
    def __init__(self, parent=None, scntoc_object=None):
        QtGui.QDialog.__init__(self, parent)
        self._scntoc = scntoc_object

        self.resize(900, 500)

        # the main layout
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        # build the model/resolution tree
        self.tree = QtGui.QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderHidden(True)
        #self.tree.setAlternatingRowColors(True)
        self.tree.itemChanged.connect(self.itemChanged)
        layout.addWidget(self.tree)

        # the cancel/save buttons at the bottom
        button_layout = QtGui.QHBoxLayout()
        cancel_button = QtGui.QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)
        save_button = QtGui.QPushButton('Save')
        save_button.clicked.connect(self.save)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

        # finally we load the scntoc data into the tree
        self.load_tree()

    def load_tree(self):
        for model in self._scntoc.models():
            model_item = QtGui.QTreeWidgetItem([model.name()])

            model_item.setFlags(model_item.flags() |
                                QtCore.Qt.ItemIsUserCheckable |
                                QtCore.Qt.ItemIsEditable)

            if model.active_resolution().name() == 'Offloaded':
                model_item.setCheckState(0, QtCore.Qt.Unchecked)
                model_is_offloaded = True
            else:
                model_item.setCheckState(0, QtCore.Qt.Checked)
                model_is_offloaded = False

            model_item.setData(0, MODEL_ROLE, model)

            for res in model.resolutions():
                if res.name() == 'Offloaded':
                    continue

                res_item = QtGui.QTreeWidgetItem(model_item,
                                                 [res.name(), res.path()])

                res_item.setFlags(res_item.flags() |
                                  QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsEditable)
                if model_is_offloaded:
                    res_item.setDisabled(True)
                if model.active_resolution().name() == res.name():
                    res_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    res_item.setCheckState(0, QtCore.Qt.Unchecked)

                res_item.setData(0, RES_ROLE, res)
                model_item.addChild(res_item)

            self.tree.addTopLevelItem(model_item)
            model_item.setFirstColumnSpanned(True)
            model_item.setExpanded(True)

        self.tree.resizeColumnToContents(0)

    def itemChanged(self, item, column):
        if item.parent() is None:
            # this means we have a top level item, i.e. a model change
            # first we check if we changed the name of the model
            model_obj = item.data(0, MODEL_ROLE).toPyObject()
            if item.text(0) == model_obj.name():
                if item.checkState(0) == QtCore.Qt.Checked:
                    # ok, now we want to enable a model i.e. setting the
                    # resolution to something other than 0, first we should
                    # check that there are any resolutions besides 'Offloaded'
                    if len(model_obj.resolutions()) == 1:
                        # reset the checkbox to unchecked since we really cant
                        # set this to any real resolution
                        item.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        # we have at least one actual resolution, lets make it
                        # the active one
                        model_obj.set_active_resolution(1)
                        item.child(0).setCheckState(0, QtCore.Qt.Checked)
                        for i in range(item.childCount()):
                            item.child(i).setDisabled(False)
                        item.setExpanded(True)
                else:
                    # now we are marking a model to be 'Offloaded'
                    model_obj.set_active_resolution(0)
                    for i in range(item.childCount()):
                        item.child(i).setCheckState(0, QtCore.Qt.Unchecked)
                        item.child(i).setDisabled(True)
                    item.setExpanded(False)
            else:
                # so the name of the model has been changed, easy enough
                # we update the model object
                model_obj.set_name(str(item.text(0)))
        else:
            # now we are dealing with a resolution
            res_obj = item.data(0, RES_ROLE).toPyObject()
            model_obj = item.parent().data(0, MODEL_ROLE).toPyObject()

            if column == 1:
                # the resolution path has been changed, this should be checked
                # at some point for the existance of the file
                res_obj.set_href(str(item.text(1)))
            else:
                if item.text(0) == res_obj.name():
                    if item.parent().checkState(0) == QtCore.Qt.Unchecked:
                        # the parent model is offloaded, we do nothing
                        return
                    # someone checked or unchecked a resolution
                    if item.checkState(0) == QtCore.Qt.Checked:
                        # the resolution was checked, now we must
                        # make sure that if there are other sibling
                        # resolutions that they get unchecked
                        for i in range(item.parent().childCount()):
                            if item.parent().child(i) != item:
                                item.parent().child(i).setCheckState(0, QtCore.Qt.Unchecked)
                            else:
                                new_active_resolution_id = i + 1
                                if model_obj.active_resolution_id() != new_active_resolution_id:
                                    model_obj.set_active_resolution(new_active_resolution_id)
                    else:
                        for i in range(item.parent().childCount()):
                            if item.parent().child(i).checkState(0) == QtCore.Qt.Checked:
                                break
                        else:
                            item.setCheckState(0, QtCore.Qt.Checked)

                else:
                    # the name of the resolution was changed, update the
                    # resolution object
                    res_obj.set_name(str(item.text(0)))

    def save(self):
        try:
            self._scntoc.write()
        except Exception, err:
            print 'Unable to save scntoc:', err
        else:
            self.close()

    def show_modal(self):
        '''
            This method is from jo benayoun from the XSI mailing list.
        '''
        import ctypes
        import ctypes.wintypes
        anchor = self.parentWidget()

        ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = (ctypes.py_object, )
        ctypes.windll.user32.GetParent.argtypes = (ctypes.wintypes.HWND, )
        ctypes.windll.user32.GetParent.restype = ctypes.wintypes.HWND
        ctypes.windll.user32.EnableWindow.argtypes = (ctypes.wintypes.HWND, ctypes.wintypes.BOOL)
        ctypes.windll.user32.EnableWindow.restype = ctypes.c_int

        hwnd = ctypes.pythonapi.PyCObject_AsVoidPtr(anchor.winId().ascobject())
        hwnd = ctypes.windll.user32.GetParent(ctypes.wintypes.HWND(hwnd))
        ctypes.windll.user32.EnableWindow(hwnd, 0)
        self.exec_()
        self.close()
        ctypes.windll.user32.EnableWindow(hwnd, 1)
        ctypes.windll.user32.SetActiveWindow(hwnd)
        return None


def run_editor_gui(scntoc_object):
    app = QtGui.QApplication(sys.argv)
    w = ScntocEditor(None, scntoc_object)
    w.show()

    app.exec_()
    sys.exit()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Open scntoc file for editing')

    parser.add_argument('scntocFile', nargs=1)
    args = parser.parse_args()

    path_to_scntoc = os.path.abspath(args.scntocFile[0])

    if not os.path.exists(path_to_scntoc):
        print 'scntoc file: %s does not exist!' % path_to_scntoc
        sys.exit()

    scntoc_object = scntoc.SCNTOC.from_file(path_to_scntoc)
    run_editor_gui(scntoc_object)
