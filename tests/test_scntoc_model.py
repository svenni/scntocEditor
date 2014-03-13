import unittest
import xml.etree.ElementTree as ET

import scntoc

proper_model_xml_root = ET.Element('Model')
proper_model_xml_root.set('name', 'mega_model')
proper_model_xml_root.set('active_resolution', '1')

res0 = ET.SubElement(proper_model_xml_root, 'resolution')
res0.set('name', 'Offloaded')
res0.set('id', '0')
res0.set('href', '')

res1 = ET.SubElement(proper_model_xml_root, 'resolution')
res1.set('name', 'res1')
res1.set('id', '1')
res1.set('href', 'file://path/to/file')


class TestModel(unittest.TestCase):
    def test_creation(self):
        model = scntoc.Model('modelName')
        self.assertEquals(model.name(), 'modelName')
        self.assertEquals(len(model.resolutions()), 1)
        self.assertTrue(isinstance(model.resolutions(0), scntoc.Resolution))
        self.assertEquals(model.active_resolution_id(), 0)

    def test_getting_current_resolution(self):
        model = scntoc.Model('modelName')
        ar = model.active_resolution()
        self.assertTrue(isinstance(ar, scntoc.Resolution))
        self.assertEquals(ar.name(), 'Offloaded')
        self.assertEquals(ar.id(), 0)
        self.assertEquals(ar.href(), '')

    def test_changing_name(self):
        model = scntoc.Model('modelName')
        model.set_name('newName')
        self.assertEquals(model.name(), 'newName')

    def test_adding_resolutions_setting_active_resolution(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'path_to_file', True)
        self.assertEquals(model.active_resolution_id(), 1)
        self.assertEquals(len(model.resolutions()), 2)
        self.assertTrue(isinstance(model.resolutions(1), scntoc.Resolution))
        self.assertTrue(model.resolutions(1).name(), 'res1')
        self.assertTrue(model.resolutions(1).href(), 'file://path_to_file')

    def test_adding_resolutions_not_setting_active_resolution(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'path_to_file', False)
        self.assertEquals(model.active_resolution_id(), 0)
        self.assertEquals(len(model.resolutions()), 2)
        self.assertEquals(model.resolutions(1).name(), 'res1')
        self.assertTrue(model.resolutions(1).href(), 'file://path_to_file')

    def test_setting_active_resolution(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'file://path_to_file')
        model.add_resolution('res2', 'file://new_file')

        self.assertEquals(model.active_resolution_id(), 2)
        model.set_active_resolution(0)
        self.assertEquals(model.active_resolution_id(), 0)

    def test_setting_invalid_active_resolution(self):
        model = scntoc.Model('modelName')
        with self.assertRaises(RuntimeError):
            model.set_active_resolution(99)

    def test_getting_resolutions(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'file://path_to_file')
        model.add_resolution('res2', 'file://new_file')
        self.assertTrue(isinstance(model.resolutions(), list))
        self.assertEquals(len(model.resolutions()), 3)
        self.assertTrue(isinstance(model.resolutions(1), scntoc.Resolution))
        self.assertEquals(model.resolutions(1).name(), 'res1')

    def test_removing_resolutions(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'file://path_to_file')
        model.add_resolution('res2', 'file://new_file')

        self.assertEquals(len(model.resolutions()), 3)
        self.assertEquals(model.active_resolution_id(), 2)
        self.assertEquals(model.resolutions(0).id(), 0)
        self.assertEquals(model.resolutions(0).name(), 'Offloaded')
        self.assertEquals(model.resolutions(1).id(), 1)
        self.assertEquals(model.resolutions(1).name(), 'res1')
        self.assertEquals(model.resolutions(2).id(), 2)
        self.assertEquals(model.resolutions(2).name(), 'res2')
        model.remove_resolution('res2')
        self.assertEquals(len(model.resolutions()), 2)
        self.assertEquals(model.active_resolution_id(), 1)
        self.assertEquals(model.active_resolution().name(), 'res1')
        self.assertEquals(model.resolutions(0).id(), 0)
        self.assertEquals(model.resolutions(0).name(), 'Offloaded')
        self.assertEquals(model.resolutions(1).id(), 1)
        self.assertEquals(model.resolutions(1).name(), 'res1')

    def test_removing_not_last_resolution(self):
        model = scntoc.Model('modelName')
        model.add_resolution('res1', 'file://path_to_file')
        model.add_resolution('res2', 'file://new_file')

        model.remove_resolution('res1')
        self.assertEquals(model.resolutions(0).id(), 0)
        self.assertEquals(model.resolutions(0).name(), 'Offloaded')
        self.assertEquals(model.resolutions(1).id(), 1)
        self.assertEquals(model.resolutions(1).name(), 'res2')
        self.assertEquals(len(model.resolutions()), 2)
        self.assertEquals(model.active_resolution_id(), 1)

    def test_removing_invalid_resolution(self):
        model = scntoc.Model('modelName')
        with self.assertRaises(RuntimeError):
            model.remove_resolution('badRes')

    def test_removing_offloaded_resolution(self):
        model = scntoc.Model('modelName')
        with self.assertRaises(RuntimeError):
            model.remove_resolution('Offloaded')
        with self.assertRaises(RuntimeError):
            model.remove_resolution('offloaded')


class TestModelXML(unittest.TestCase):
    def test_from_xml(self):
        model = scntoc.Model.from_xml(proper_model_xml_root)
        self.assertTrue(isinstance(model, scntoc.Model))
        self.assertEquals(model.name(), 'mega_model')
        self.assertEquals(model.active_resolution_id(), 1)
        self.assertEquals(len(model.resolutions()), 2)
        self.assertEquals(model.resolutions(0).name(), 'Offloaded')
        self.assertEquals(model.active_resolution().href(), 'file://path/to/file')

    def test_to_xml(self):
        model = scntoc.Model('mega_model')
        model.add_resolution('res1', 'file://path/to/file')

        xml = model.xml()
        self.assertEquals(xml.attrib, proper_model_xml_root.attrib)
        self.assertEquals(len(xml), 2)

        self.assertEquals(xml[0].attrib, res0.attrib)
