import unittest
from model import campaign, campaign_type, ctypes
from utils import init_db

__author__ = 'rohan'

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_campaigns(self):
        db = init_db()
        new_campaign = campaign(desc="Test Campaign")
        db.add(new_campaign)
        db.commit()
        request = db.query(campaign).filter_by(desc="Test Campaign").first()
        print request.desc
        self.assertTrue(request.desc is new_campaign.desc)

    def test_campaign_types(self):
        db = init_db()
        for obj in db.query(campaign_type).order_by(campaign_type.id):
            print obj.desc
            self.assertTrue(obj.desc in ctypes)

    def test_merge(self):
        new_campaign = campaign(desc="Test Campaign")

    def test_profile(self):
        return true

if __name__ == '__main__':
    unittest.main()
