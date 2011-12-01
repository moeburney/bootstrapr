import json
import pickle
import unittest
from model import init_db, campaign, campaign_type, ctypes, drop_all, CHAT_EMAIL, makechatfromemail, profile, chat, get_timeline, get_data_point

__author__ = 'rohan'

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)
    def test_timeline(self):
        get_timeline(1,2)
        get_data_point(1,2,1321170000)
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
        return True
    def test_email_tree(self):
        input = open("data.pkl","rb")
        mail = pickle.load(input)
        for y in mail:
            print "=======######## GOt email "+(y['subject'] if 'subject' in y else "NO SUBJECT") +"  mid "+(y['id'] if 'id' in y else "NO ID") + "  parent id "+(y['parent'] if ('parent' in y and y['parent'] is not None) else "NO PARENT")
            db = init_db()
            contact = db.query(profile).filter(profile.pemail == "moeburney@gmail.com").first()
            currchat = makechatfromemail(y)
            if not contact.chats:
                currchat.save(session=db)
                contact.chats.append(currchat)
                contact.save(session=db)
                print "save single email"
                continue
            contact.chats.sort(key=lambda x:x.ts)
            for old in contact.chats:
                obj = json.loads(old.details)
                if obj['id'] == y['id']:
                    continue
                if old.type == CHAT_EMAIL:

                    print "OLD email "+(obj['subject'] if 'subject' in obj else "NO SUBJECT") +"  mid "+(obj['id'] if 'id' in obj else "NO ID" )+ "  parent id "+(obj['parent'] if ('parent' in obj and  obj['parent'] is not None) else "NO PARENT")
                    if obj['id'] == (y['parent'] if 'parent' in y else ""):
                        print "EMAIL " + y['id'] + " is reply to " + old['id']
                        old.replies.append(currchat)
                        old.save(session=db)
                        currchat.save(session=db)
                        contact.chats.append(currchat)
                        contact.save(session=db)
                        continue
                    currchat.save(session=db)
                    contact.chats.append(currchat)
                    contact.save(session=db)
        return True
    def test_data(self):
        db = init_db()
        chats = db.query(chat)
        for c in chats:
            obj = json.loads(c.details)
            if 'body' in obj:
                if 'And about the gain and expenses' in obj['body']:
                    print c.id
        return True
if __name__ == '__main__':
    unittest.main()
