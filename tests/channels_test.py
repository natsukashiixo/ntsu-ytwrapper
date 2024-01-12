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

# test values
def test_resp_class_first_item_is_correct():
    assert TEST_RESP.first_item() == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_item_by_index_is_correct():
    assert TEST_RESP.item_by_index(0) == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_item_by_kwp_is_correct():
    assert TEST_RESP.item_by_snippet_kwp('channelTitle', 'Rick Astley') == {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}}

def test_resp_class_all_items_in_correct():
    assert TEST_RESP.all_items() == [
    {'snippet': {'channelTitle': 'Rick Astley',
                 'channelID': 'UCuAXFkgsw1L7xaCfnd5JJOw'}},
    {'snippet': {'channelTitle': 'Not Rick Astley',
                 'channelID': 'UCuABABABABABABABnABABAB'}}
    ]