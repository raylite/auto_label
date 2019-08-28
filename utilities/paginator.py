#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 17:49:23 2019

@author: ja18581
"""

class PageResult:
    def __init__(self, data, page = 0, number = None, list_paging = False):
        self.data = data
        if list_paging:
            self.page_tuple = self.neighborhood2()
        else:
            self.page_tuple = self.neighborhood()
        self.number = number
        self.page = page
        
        
    def list_on_page(self):
        return(self.data[self.page])
        
    def has_next(self):
        if self.page + 1 < len(self.data):
            return True
        else:
            return False
    
    def has_prev(self):
        if self.page > 0 and self.page < len(self.data):
            return True
        else:
            return False
        
    
    def next_tuple(self):
        self.pages = (next(self.page_tuple))
        print(self.pages)
        
    def next_page(self):
        if self.page < len(self.data):
            return self.page + 1
        else:
            return None
    
    def prev_page(self):
        if self.page < len(self.data):
            return self.page - 1
        else:
            return None
    
    def neighborhood2(self):
        iterator = iter(range(len(self.data)))
        prev_item = None
        #current_item = next(iterator)  # throws StopIteration if empty.
        for next_item in iterator:
            yield (prev_item, next_item)
            prev_item = next_item
            #current_item = next_item
        yield (prev_item, None)
    
    def neighborhood(self):
        iterator = iter(range(len(self.data)))
        prev_item = None
        current_item = next(iterator)  # throws StopIteration if empty.
        for next_item in iterator:
            yield (prev_item, current_item, next_item)
            prev_item = current_item
            current_item = next_item
        yield (prev_item, current_item, None)
