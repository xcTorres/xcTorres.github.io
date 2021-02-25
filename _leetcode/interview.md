import math
import pandas as pd
import numpy as np
from typing import List

"""
Q1.
There are lots of fraud users who create a lot of accounts to get vouchers from Shopee. To solve that problem, Shopee DS member come up with a algorithm which can detect same user:
That is to see whether two users have similar usernames. If the minimum edit distance of two usernames is below a certain threshold, we call these two accounts belong to the same user. Please implement the function below to find the minimum edit distance between two usernames.
(Assume insertion, deletion or substitution are of same cost)
"""

def find_min_edit_distance(u1: str, u2: str) -> int:
    """
    function to get minimum edit distance between two username strings
    Args:
        u1: username 1
        u2: username 2

    Returns:
        min_edit_distance
    
    Example:
        u1="shopee", u2="soap" -> min_edit_distance=4
    """
    # test for
    # no change "soap" -> "soap"
    # deletion "shopee" -> "soap"
    # issue when characters already exist in str "soeapee" -> "soap"
        # delete 3 e's, instead of doing substitution.
    # issue when characters already exist in str "soeepee" -> "soap"
        # delete 3 e's, replace 1 e with a instead of doing substitution
    # issue when characters already exist in str "saoepee" -> "soap"
        # delete 3 e's, replace 1 e with a instead of doing substitution
    
    
    # try to make longer string match shorter string
    if len(u2) >= len(u1):
        longstr, shortstr = u2, u1
    else:
        longstr, shortstr = u1, u2
    
    if longstr == shortstr:
        return 0
    
    else:
        if longstr[0] == shortstr[0]:
            return find_min_edit_distance(longstr[1:], shortstr[1:])
        else:
            #longstr[0] = shortstr[0] # replacement
            #longstr = longstr[1:] # deletion
            #longstr = shortstr[0]+longstr # insertion
            return min(find_min_edit_distance(longstr[1:], shortstr) +1, # deletion
                       find_min_edit_distance(shortstr[0]+longstr, shortstr) +1, # deletion
                       find_min_edit_distance(shortstr[0] + longstr[1:], shortstr) +1) # replacement
        


"""
Q2.
Now we know if two users have very similar usernames using edit distance in Q1. In addition, we also would like to guess the hidden pattern when a user creates multiple accounts with similar usernames. Assume a user creates his first account with a certain username, and every new account he creats subsequently is by replacing one and only one character of the previous username (without changing the length). Now we have two known usernames (start_username and end_username) of the user and a list of candidate usernames (includes start_username and end_username), we would like to know what's the minimum number of usernames in the candidate list which are potentially accounts created by him by finding the length of shortest transformation sequence. Please implement the function below to find the length of shortest transformation sequence.
"""

def find_min_trans_seq_len(start_username: str, end_username: str, candidate_usernames: List[str]) -> int:
    """
    function to get minimum trans seq between two username strings
    Args:
        start_username: the first username created by the user
        end_username: the last username created by the user
        candidate_usernames: the list of candidate usernames which contains possible usernames created by the same user

    Returns:
        min_trans_seq_len
    
    Example:
        Input: start_username = "shopee", 
               end_username = "sloppy", 
               candidate_usernames = ["shopee", "shopey","shoppy","sloppy","shopaa","shapee","slopee"]
        Output: 4
        Explanation: As one shortest transformation is "shopee" -> "shopey" -> "shoppy" -> "sloppy", return its length 4.

    """
    def dist(a,b):
        score = 0
        for i,j in zip(a,b):
            if i!=j:
                score+=1
        return score
    
    # create an organised seq of series of changes, return index of end_username
    seq = [start_username]
    cur = start_username
    
    while candidate_usernames != []:
        for name in candidate_usernames:
            if dist(cur, name) == 1: # define dist to know that only 1 char was changed
                seq.append(name)
                cur = name
                candidate_usernames.pop(name)
                break
    
    return seq.index(end_username) + 1
        
    



"""
Q3.
[This is a case question, no code is required] To find out potential fraudulent users, analyzing a user’s browsing behaviour is helpful. We have obtained many Shopee users’ in-app browsing records and stored in our database, an example:

userid  |  visited_page_type  |  timestamp
-------------------------------------------
123456  |  home               |  1609430400
123456  |  search             |  1609430410
123456  |  product            |  1609430415  
...
654321  |  home               |  1609512600
654321  |  flashsale          |  1609512605
654321  |  payment            |  1609512610
...

Now we would like to design a system to quickly find out users who have visited similar pages (not necessarily exact match):

Input: an userid

Output: an list of userids with similar visited pages

Questions:

1) If the page browsing sequence IS NOT important, how would you design the system (what’s the algorithm chosen, what’s the similarity metrics, what’s the main components of your system)?

- given user | # visits to home/search/... page, do clustering



2) If the page browsing sequence IS important, how would you design the system?

- design common user behaviour funnels, see which funnels users fall into
    home -> search -> product
    flashsale -> payment
    


"""