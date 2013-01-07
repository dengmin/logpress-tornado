#!/usr/bin/env python
#coding=utf8
from datetime import datetime
from markdown import Markdown

markdowner = Markdown()

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
	return value.strftime(format)

def truncate_words(s, num=50, end_text='...'):
	s = unicode(s,'utf8')
	length = int(num)
	if len(s) > length:
		s = s[:length]
		if not s[-1].endswith(end_text):
			s= s+end_text
	return s

def mdconvert (value):
	return markdowner.convert(value)

def null(value):
	return value if value else ""


def register_filters():
	filters ={}
	filters['truncate_words']=truncate_words
	filters['datetimeformat']=datetimeformat
	filters['markdown']=mdconvert
	filters['null']=null
	return filters