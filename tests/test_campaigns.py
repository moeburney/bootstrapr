from sqlalchemy.schema import MetaData
from base import Base
from dbutils import engine
import dbutils
from campaign import init_db
from models.campaign import campaign
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from utils.dbutils import Session

__author__ = 'rohan'

import unittest

class MyTestCase(unittest.TestCase):

    def test_something(self):
        self.assertEqual(True, True)
    def test_campaigns(self):
        db = init_db()
        new_campaign = campaign(desc="Test Campaign")
        db.add(new_campaign)
        request = db.query(campaign).filter_by(desc="Test Campaign").first()
        self.assertTrue(request.desc == new_campaign.desc)
if __name__ == '__main__':
    unittest.main()
