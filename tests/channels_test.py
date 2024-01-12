import datetime
from ntsuwrap import YoutubeTokenBucket
from ntsuwrap import ChannelsDotList
from ntsuwrap import ParseChannels

BUCKET = YoutubeTokenBucket(1) #shouldnt need more than 1 so guess this also works as a rudimentary test for the bucket class if ran online
TEST_RESP = ChannelsDotList('not_an_api_key', 'UCuAXFkgsw1L7xaCfnd5JJOw', BUCKET)

#obv just save an actual response instead of this. its just for overview
_4_the_lulz = {'items': [
    {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}},
    {'snippet': {'channelTitle': 'Not Rick Astley',
                 'channelID': 'UCuABABABABABABABnABABAB'}}
    ]}

#should separate the typecheckers into a separate file eventually since they're designed to check on an actual API response where the values you get are unknown
def test_resp_class_first_item_is_dict():
    assert TEST_RESP.first_item() == type(dict)

def test_resp_class_item_by_index_is_dict():
    assert TEST_RESP.item_by_index(0) == type(dict)

def test_resp_class_item_by_kwp_is_dict():
    assert TEST_RESP.item_by_snippet_kwp('channelTitle', 'Rick Astley') == type(dict)

def test_resp_class_all_items_is_list():
    assert TEST_RESP.all_items() == type(list)

# test values of sample response
def test_resp_class_first_item_is_correct():
    assert TEST_RESP.first_item() == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_item_by_index_is_correct():
    assert TEST_RESP.item_by_index(0) == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_item_by_kwp_is_correct():
    assert TEST_RESP.item_by_snippet_kwp('channelTitle', 'Rick Astley') == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_all_items_is_correct():
    assert TEST_RESP.all_items() == [
    {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}},
    {'snippet': {'channelTitle': 'Not Rick Astley',
                 'channelID': 'UCuABABABABABABABnABABAB'}}
    ]

#type check parsing of live API response
DA_DICT = TEST_RESP.first_item()
pdd = ParseChannels(DA_DICT) #pdd means parse da dict :^)

def test_get_name_is_str():
    assert pdd.get_name() == type(str)

def test_get_desc_is_str():
    assert pdd.get_desc() == type(str)

def test_get_pfp_default_is_str():
    assert pdd.get_pfp() == type(str)

def test_get_pfp_explicit_default_is_str():
    assert pdd.get_pfp('default') == type(str)

def test_get_pfp_medium_is_str():
    assert pdd.get_pfp('medium') == type(str)

def test_get_pfp_high_is_str():
    assert pdd.get_pfp('high') == type(str)

def test_get_createtime_is_datetime():
    assert pdd.get_createtime() == type(datetime)

def test_get_url_is_str():
    assert pdd.get_url() == type(str)

def test_get_privacystatus_is_str():
    assert pdd.get_privacystatus() == type(str)

def test_get_subscribers_is_int():
    assert pdd.get_subscribers() == type(int)

def test_get_channel_views_is_int():
    assert pdd.get_channel_views() == type(int)

def test_get_vidcount_is_int():
    assert pdd.get_vidcount() == type(int)

#test correct values of parsing using a sample response
#because i don't yet have a sample response i'll just have to fill this out with generics
    
psr = ParseChannels({}) #psr means parse sample response :^)

def test_get_name_is_correct():
    assert pdd.get_name() == ''

def test_get_desc_is_correct():
    assert pdd.get_desc() == ''

def test_get_pfp_default_is_correct():
    assert pdd.get_pfp() == ''

def test_get_pfp_explicit_default_is_correct():
    assert pdd.get_pfp('default') == ''

def test_get_pfp_medium_is_correct():
    assert pdd.get_pfp('medium') == ''

def test_get_pfp_high_is_correct():
    assert pdd.get_pfp('high') == ''

def test_get_createtime_is_correct():
    assert pdd.get_createtime() == datetime.datetime.now()

def test_get_url_is_correct():
    assert pdd.get_url() == ''

def test_get_privacystatus_is_correct():
    assert pdd.get_privacystatus() == ''

def test_get_subscribers_is_correct():
    assert pdd.get_subscribers() == 0

def test_get_channel_views_is_correct():
    assert pdd.get_channel_views() == 0

def test_get_vidcount_is_correct():
    assert pdd.get_vidcount() == 0

#write tests designed to fail here i guess?