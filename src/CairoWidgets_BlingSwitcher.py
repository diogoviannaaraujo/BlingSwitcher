import gtk
import cairo
import wnck
class BlingSwitcher(gtk.DrawingArea):

	import gconf

	client = gconf.client_get_default()

	bgpixbuf = ""
	bgpixbuf_for_squared = ""
	bgurl = ""
	bgurl2 = ""
	height = 60
	width = 80
	selected = 0
	bg_r = ""
	bg_g = ""
	bg_b = ""
	bg_a = ""

	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.connect("expose_event", self.expose)
		self.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK)
		self.connect("motion-notify-event", self.motion_notify)
		self.connect('button-press-event', self.button_press)
		self.set_size_request(self.draw_for_all_viewports_width(self.width),self.draw_for_all_viewports_height(self.height))

	############################################################# Configuration

	def set_thumb_size(self,w,h):
		self.width = w
		self.height = h

	def set_bg_rgba(self,r,g,b,a):
		self.bg_r = r
		self.bg_g = g
		self.bg_b = b
		self.bg_a = a


	############################################################# Event Functions


	def expose(self, widget, event):
		self.context = self.new_transparent_cairo_window(self)
		self.draw_for_all_viewports(self.context,self.width,self.height,self.selected)
		return False

	def motion_notify(self,widget,event):
		(pointer_x, pointer_y) = widget.get_pointer()
		vpnumberx = self.get_viewport_cols()
		vpnumbery = self.get_viewport_rows()
#		print "pointer_y %d pointer_x %d" % (pointer_y,pointer_x)
		for j in range(1, vpnumbery+1):
			for i in range(1, vpnumberx+1):
				if (pointer_x > ((i-1)*(self.width+10))) & (pointer_x < (i*(self.width+10)-10)) & (pointer_y > ((j-1)*(self.height+10))) & (pointer_y < (j*(self.height+10)-10)):
					if (self.selected != i+vpnumberx*(j-1)):
						self.selected = i+vpnumberx*(j-1)
						#print  i+vpnumberx*(j-1)
						widget.queue_draw()

		return False

	def button_press(self,widget,event):
		scr = wnck.screen_get_default()
		row = (self.selected-1) / self.get_viewport_cols()
		col = self.selected - self.get_viewport_cols()*row - 1
		#print "row %d, col %d, scr.get_width() %d" % (row, col, scr.get_width())
		scr.move_viewport(scr.get_width()*col, scr.get_height()*row)

	############################################################## Drawing Funtions

	def new_transparent_cairo_window(self,widget):
		cr = widget.window.cairo_create()
		cr.save()
		cr.set_source_rgba(self.bg_r, self.bg_g, self.bg_b, 0.85)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.restore()
		return cr

	def draw_for_all_viewports(self,context,w,h,selectedn):
		context.save()
		vpnumberx = self.get_viewport_cols()
		vpnumbery = self.get_viewport_rows()
		for j in range(1, vpnumbery+1):
			for i in range(1, vpnumberx+1):
				selected = False
				if (selectedn == i+self.get_viewport_cols()*(j-1)):
					selected = True
#					print selectedn
				self.draw_complete_thumb(context, w, h, (w+10)*(i-1), (h+10)*(j-1), i+vpnumberx*(j-1), selected, False)
		context.restore()

	def draw_for_all_viewports_width(self,w):
		vpnumberx = self.get_viewport_cols()
		return vpnumberx*(w+10)-10

	def draw_for_all_viewports_height(self,h):
		vpnumbery = self.get_viewport_rows()
		return vpnumbery*(h+10)-10

	def draw_complete_thumb(self, context, w, h, x, y, n, selected, squared):
		context.save()
		if selected == False:
			self.draw_retangle_with_background(context, w, h, x, y,n, squared)
		if selected == True:
			self.draw_retangle_with_background_over(context, w, h, x, y,n, squared)
		self.draw_circle_with_number(context, n, x+w/2, y+h/2)
		context.restore

	def draw_retangle_with_background_over(self, context, w, h, x, y, n,squared):
		context.save()
		context.translate(x,y)
		self.DrawRoundedRectangle(context,0,0,w,h,11)
		context.clip()
		context.new_path()
		if (self.check_for_background() == True):
			pixbuf = self.get_pixbuf_background(w, h,squared)
			context.set_source_pixbuf(pixbuf,0,0)
		if (self.check_for_background() == False):
			context.set_source_rgba(self.get_background_color('r'), self.get_background_color('g'), self.get_background_color('b'))
		self.DrawRoundedRectangle(context,1,1,w-1,h-1,11)
		context.fill()
		self.draw_windows(context,w,h,n)
		self.draw_reflection(context, w, h)
		context.set_line_width(2)
		context.set_source_rgba (0.12, 0.12, 0.12, 1);
		self.DrawRoundedRectangle(context,1,1,w-1,h-1,11)
		context.stroke()
		context.restore()

	def draw_retangle_with_background(self, context, w, h, x, y,n,squared):
		context.save()
		context.translate(x,y)
		self.DrawRoundedRectangle(context,0,0,w,h,11)
		context.clip()
		context.new_path()
		if (self.check_for_background() == True):
			pixbuf = self.get_pixbuf_background(w, h,squared)
			context.set_source_pixbuf(pixbuf,0,0)
		if (self.check_for_background() == False):
			context.set_source_rgba(self.get_background_color('r'), self.get_background_color('g'), self.get_background_color('b'))
		self.DrawRoundedRectangle(context,1,1,w-1,h-1,11)
		context.fill()
		self.draw_windows(context,w,h,n)
		self.draw_reflection(context, w, h)
		context.set_line_width(2)
		context.set_source_rgba (0.5, 0.5, 0.5, 0.9);
		self.DrawRoundedRectangle(context,1,1,w-1,h-1,11)
		context.stroke()
		context.restore()

	def draw_reflection(self, context, w, h):
		context.save()
		context.set_source_rgba(1,1,1,0.4)
		context.move_to(0, 12)
		context.curve_to(0,0,0,0,12,0)
		context.line_to(w-12,0)
		context.curve_to(w,0,w,0,w,12)
		context.curve_to(w/4,6, w/4, 12, 0, 20)
		context.line_to(0,12)
		context.close_path()
		context.fill()
		context.stroke()
		context.restore()

	def draw_on_square(self,context,n,side):
		context.save()
		thumbheight = (side/4)*3
		start = (side-thumbheight)/2
		context.translate(0,start)
		self.draw_complete_thumb(context, side, thumbheight, 0, 0, n, True, True)
		context.restore()

	def draw_circle_with_number(self, ct, number, x, y):
		ct.save()
		ct.set_source_rgba (0.1, 0.1, 0.1, 0.85);
		ct.arc (x, y, 10.0, 0, 2*3.1415);
		ct.fill ();
		ct.select_font_face ("Sans", cairo.FONT_WEIGHT_BOLD)
		ct.set_source_rgba (1, 1, 1, 1);
		ct.set_font_size(14)
		ct.move_to(x-4,y+5)
		ct.show_text(str(number))
		ct.restore()


	def draw_windows(self,context,w,h,n):
		# Fonction a modifier pour l affichage sur plusieurs lignes
		scr = wnck.screen_get_default()
		(scrw, scrh) = (scr.get_width(), scr.get_height())
		windows = scr.get_windows_stacked()
		for window in windows:
			if (window.is_minimized() != True) & (window.is_skip_pager() != True):
				(winx, winy, winw, winh) = window.get_geometry()
				(winx, winy, winw, winh) = (float(winx)/scrw*w, float(winy)/scrh*h, float(winw)/scrw*w, float(winh)/scrh*h)
				if (n == self.get_active_viewport_number()):
					if (winx < w) & (winx > -1):
						if (winx+winw > w-1):
							winw = (w-winx)-2
						if (winy+winh > h-1):
							winh = (h-winy)-2
						context.save()
						context.set_source_rgba(0.85,0.85,0.85,0.8)
						context.rectangle(winx,winy,winw,winh)
						context.fill()
						context.set_source_rgba(0.1,0.1,0.1,1)
						context.set_line_width(1)
						context.rectangle(winx,winy,winw,winh)
						context.stroke()
						context.restore()
				else:
					winx = winx-w*(n-self.get_active_viewport_number())
					if (winx < w) & (winx > -1):
						if (winx+winw > w-1):
							winw = (w-winx)-2
						if (winy+winh > h-1):
							winh = (h-winy)-2
						context.save()
						context.set_source_rgba(1,1,1,0.4)
						context.rectangle(winx,winy,winw,winh)
						context.fill()
						context.set_source_rgba(0.1,0.1,0.1,0.9)
						context.set_line_width(1)
						context.rectangle(winx,winy,winw,winh)
						context.stroke()
						context.restore()

	def get_pixbuf_background(self, w, h, squared):
		if (squared == False):
			url = self.client.get_string('/desktop/gnome/background/picture_filename')
	    		if (self.bgurl != url):
				self.bgurl = url
				self.bgpixbuf = gtk.gdk.pixbuf_new_from_file(url)
				self.bgpixbuf = self.bgpixbuf.scale_simple(w,h, gtk.gdk.INTERP_TILES)
			return self.bgpixbuf
		else:
			url2 = self.client.get_string('/desktop/gnome/background/picture_filename')
	    		if (self.bgurl2 != url2):
				self.bgurl2 = url2
				self.bgpixbuf_for_squared = gtk.gdk.pixbuf_new_from_file(url2)
				self.bgpixbuf_for_squared = self.bgpixbuf_for_squared.scale_simple(w,h, gtk.gdk.INTERP_TILES)
			return self.bgpixbuf_for_squared

	def get_background_color(self, c):
		color = self.client.get_string('/desktop/gnome/background/primary_color')
		if (c == 'r'):
			return int(color[1:5], 16)/65335.0
		if (c == 'g'):
			return int(color[5:9], 16)/65335.0
		if (c == 'b'):
			return int(color[9:13], 16)/65335.0

	def check_for_background(self):
		url = self.client.get_string('/desktop/gnome/background/picture_filename')
		if (url == ""):
			return False
		else:
			return True

	def DrawRoundedRectangle(self,ct,x0,y0,x1,y1,radius):
		ct.move_to(x0, y0+radius)
		ct.curve_to(x0,y0,x0,y0,x0+radius,y0)
		ct.line_to(x1-radius,y0)
		ct.curve_to(x1,y0,x1,y0,x1,y0+radius)
		ct.line_to(x1,y1-radius)
		ct.curve_to(x1,y1,x1,y1,x1-radius,y1)
		ct.line_to(x0+radius,y1)
		ct.curve_to(x0,y1,x0,y1,x0,y1-radius)
		ct.close_path()

	######################################################################## Wnck Related Functions


	def get_viewport_cols(self):
		scr = wnck.screen_get_default()
		while gtk.events_pending():
			gtk.main_iteration()
		wrkspace = scr.get_active_workspace()
		nviewp = wrkspace.get_width()/scr.get_width()
		return nviewp

	def get_viewport_rows(self):
		scr = wnck.screen_get_default()
		while gtk.events_pending():
			gtk.main_iteration()
		wrkspace = scr.get_active_workspace()
		mviewp = wrkspace.get_height()/scr.get_height()
		return mviewp

	def get_active_viewport_number(self):
		scr = wnck.screen_get_default()
		while gtk.events_pending():
			gtk.main_iteration()
		wrkspace = scr.get_active_workspace()
		nviewp = (wrkspace.get_viewport_x() + scr.get_width())/scr.get_width()
		mviewp =  wrkspace.get_viewport_y()/scr.get_height()*self.get_viewport_cols()
		return nviewp+(self.get_viewport_rows()-1)*mviewp

	def move_viewport(self, direction):
		#print "selected %d, viewport_number %d, get_viewport_cols %d, get_viewport_cols %d" % (self.selected, self.get_active_viewport_number(), self.get_viewport_cols(), self.get_viewport_rows())
		if direction == 'prev':
			if self.get_active_viewport_number() != self.get_viewport_cols()*self.get_viewport_rows():
				self.selected = self.get_active_viewport_number() + 1
			else:
				self.selected = 1
		if direction == 'next':
			if  self.get_active_viewport_number() != 1:
				self.selected = self.get_active_viewport_number() - 1
			else:
				self.selected = self.get_viewport_cols()*self.get_viewport_rows()
		scr = wnck.screen_get_default()
		row = (self.selected-1) / self.get_viewport_cols()
		col = self.selected - self.get_viewport_cols()*row - 1
		#print "selected %d, row %d, col %d,get_viewport_cols %d, get_viewport_cols %d" % (self.selected, row, col, self.get_viewport_cols(), self.get_viewport_rows())
		scr.move_viewport(scr.get_width()*col, scr.get_height()*row)

