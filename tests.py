import unittest
from model import init_db, campaign, campaign_type, ctypes, drop_all

__author__ = 'rohan'

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_campaigns(self):
        drop_all()
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
        return True

if __name__ == '__main__':
    unittest.main()
