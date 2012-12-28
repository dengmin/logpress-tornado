#!/usr/bin/env python
#coding=utf8

from jinja2 import FileSystemLoader
from handlers import BaseHandler
from models import Post,Category,Tag,Link,Comment
import os
from lib.pagination import Pagination
import peewee
from peewee import fn
from peewee import RawQuery
from tornado.web import StaticFileHandler
from database import db
from lib.mail.message import EmailMessage,TemplateEmailMessage
from playhouse.signals import connect, post_save

class BlogHandler(BaseHandler):

	@property
	def redis(self):
		return self.application.redis

	def get_recent_posts(self):
		return Post.select().paginate(1,5)

	def get_random_posts(self):
		if isinstance(db.database,peewee.SqliteDatabase):
			return Post.select().order_by(fn.Random()).limit(5)
		else:
			return Post.select().order_by(fn.Rand()).limit(5)

	def get_category(self):
		return Category.select()

	def get_tagcloud(self):
		return Tag.select(Tag,fn.count(Tag.name).alias('count')).group_by(Tag.name)

	def get_links(self):
		return Link.select()

	def get_archives(self):
		if isinstance(db.database,peewee.SqliteDatabase):
			return RawQuery(Post,"select strftime('%Y年-%m月',created) month,sum(id) count from posts group by month")
		elif isinstance(db.database,peewee.MySQLDatabase):
			return RawQuery("select date_format(created,'%Y年-%m月') month,count(id) count from posts group by month")
		return None

	def get_calendar_widget(self):
		pass

	def get_recent_comments(self):
		return Comment.select().order_by(Comment.created.desc()).limit(5)

	def render(self,template_name,**context):
		tpl = '%s/%s'%(self.settings.get('theme_name'),template_name)
		return BaseHandler.render(self,tpl,**context)

class IndexHandler(BlogHandler):
	def get(self,page=1):
		p = self.get_argument('p',None)
		if p:
			post = Post.get(id=int(p))
			post.readnum += 1
			post.save()
			self.render('post.html',post=post)
		else:
			pagination = Pagination(Post.select(),int(page),per_page=8)
			self.render('index.html',pagination=pagination)

class PostHandler(BlogHandler):
	def get(self,postid):
		post = self.get_object_or_404(Post,id=int(postid))
		post.readnum += 1
		post.save()
		self.render('post.html',post=post)

class CategoryHandler(BlogHandler):
	def get(self,name,page=1):
		posts = Post.select().join(Category).where(Category.name=='python')
		pagination = Pagination(posts,int(page),per_page=8)
		self.render('archive.html',pagination=pagination,name=name,obj_url='/category/%s'%(name),flag='category')


class TagHandler(BlogHandler):
	def get(self,tagname,page=1):
		tags = Tag.select().where(Tag.name==tagname)
		postids = [tag.post for tag in tags]
		pagination = Pagination(Post.select().where(Post.id << postids),int(page),per_page=8)
		self.render('archive.html',pagination=pagination,name=tagname,obj_url='/tag/%s'%(tagname),flag='tag')


class FeedHandler(BaseHandler):
	def get(self):
		posts = Post.select().paginate(1, 10)
		self.set_header("Content-Type", "application/atom+xml")
		self.render('feed.xml',posts=posts)

class CommentFeedHandler(BaseHandler):
	def get(self,postid):
		self.set_header("Content-Type", "application/atom+xml")
		post = Post.get(id=int(postid))
		self.render('comment_feed.xml',post=post)

class PostCommentHandler(BaseHandler):

	@property
	def mail_connection(self):
		return self.application.email_backend

	def post(self):
		postid = self.get_argument('comment_post_ID')
		author = self.get_argument('author',None)
		email = self.get_argument('email',None)
		url = self.get_argument('url',None)
		comment = self.get_argument('comment',None)
		parent_id = self.get_argument('comment_parent',None)

		@connect(post_save,sender=Comment)
		def send_email(model_class, instance,created):
			if instance.parent_id == '0':
				message = TemplateEmailMessage(u"收到新的评论",'mail/new_comment.html',
					self.settings['smtp_user'],to=[self.settings['smtp_user']],connection=self.mail_connection)
			else:
				message = TemplateEmailMessage(u"评论有新的回复",'mail/reply_comment.html',
					self.settings['smtp_user'],to=[instance.email],connection=self.mail_connection)
			message.send()

		if postid:
			post = Post.get(id=int(postid))
			if author and email and comment:
				comment = Comment.create(post=post,ip=self.request.remote_ip,
					author=author,email=email,website=url,
					content=comment,parent_id=parent_id)
				return self.redirect(comment.url)
			else:
				self.flash(u"请填写必要信息(姓名和电子邮件和评论内容)")
				self.redirect("%s#respond"%(post.url))

routes = [
	(r"/", IndexHandler),
	(r'/page/(\d+)',IndexHandler),
	(r'/post/post-(\d+).html',PostHandler),
	(r'/tag/(\w+)',TagHandler),
	(r'/tag/(\w+)/(\d+)',TagHandler),
	(r'/category/(\w+)',CategoryHandler),
	(r'/category/(\w+)/(\d+)',CategoryHandler),
	(r'/feed',FeedHandler),
	(r'/archive/(\d+)/feed',CommentFeedHandler),
	(r'/post/new_comment',PostCommentHandler),
]