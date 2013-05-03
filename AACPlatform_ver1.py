#!/bin/env python2.7
# -*- coding: utf-8 -*-

import wxversion
wxversion.select('2.8')

import os
import time

import wx
import wx.lib.buttons as bt
from wx.lib.pubsub import Publisher #we use publisher / subscriber paradigm to communicate between classes

from string import maketrans
from pygame import mixer

###############################################################################################################################
###############################################################################################################################

### This is just the first version of one part of ATPlatform- AACPlatform (Augmentative and Alternative Communication Platform)
### In recent week (06.05-11.05) we're going to put on git second version of AACPlatform with symbolic languages support and first version of ATPlatform with games and mouse coursor support.

###############################################################################################################################
###############################################################################################################################
		

#=============================================================================
class speller(wx.Frame):
	def __init__(self, parent, id):

		wx.Frame.__init__( self , parent , id , 'ATPlatform Speller' )
		self.Maximize( True )
		self.winWidth, self.winHight = self.GetSize()
		style = self.GetWindowStyle()
		self.SetWindowStyle( style | wx.STAY_ON_TOP )
		self.Centre()
		self.MakeModal( True )
		self.SetBackgroundColour( 'black' )
		self.parent = parent
                
		self.initializeParameters()			
		self.initializeBitmaps()
		self.createGui()								
		self.initializeTimer()					
		self.createBindings()						

	#-------------------------------------------------------------------------
	def initializeParameters(self):
		self.timeGap = 2000

		self.labels = 'A B C D E F G H I J K L M N O P R S T U W Y Z SPECIAL_CHARACTERS UNDO SPEAK SAVE SPACJA OPEN EXIT'.split()

		self.flag = 'row'						
		self.numberOfRows = 4
		self.numberOfColumns = 8
		self.rowIteration = 0						
		self.colIteration = 0							
		self.count = 0										
		self.countMax = 2									
		self.numberOfPresses = 0
		
		self.typingSound = wx.Sound('a.wav')
		self.textColor = 'black'
		self.backgroundColor = 'white'
		self.scanningColor =  '#E7FAFD'#'#EFFFFF' '#'#A7EBEF'
		self.selectionColor = '#9EE4EF' #'#EFFFFF' #'#D5FAFC' #DEDBDB'

	#-------------------------------------------------------------------------
        def initializeBitmaps(self):
            
            labelFiles = ['./icons/special_characters.png', './icons/undo.png', './icons/speak.png', './icons/save.png', './icons/open.png', './icons/exit.png', ]
            
            self.labelBitmaps = {}
	    
	    labelBitmapIndex = [ self.labels.index( self.labels[-7] ), self.labels.index( self.labels[-6] ), self.labels.index( self.labels[-5] ), self.labels.index( self.labels[-4] ), self.labels.index( self.labels[-2] ), self.labels.index( self.labels[-1]) ]

            for labelFilesIndex, labelIndex in enumerate( labelBitmapIndex ):
		    self.labelBitmaps[ self.labels[labelIndex] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[labelFilesIndex], 'rb' )) )			
	#-------------------------------------------------------------------------	
	def createGui(self):
		self.vbox = wx.BoxSizer( wx.VERTICAL )
		self.textField = wx.TextCtrl( self, style=wx.TE_LEFT, size=( self.winWidth, self.winHight - self.winWidth/1.1 ) )
		self.textField.SetFont( wx.Font(60, wx.SWISS, wx.NORMAL, wx.NORMAL) )
		self.vbox.Add( self.textField, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3 )
		self.sizer = wx.GridBagSizer(3, 3)

		for index_1, item in enumerate( self.labels[:-7] ):
			b = bt.GenButton( self, -1, item, name=item, size=(169, 150) )
			b.SetFont( wx.Font(35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetForegroundColour( self.textColor )
			b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( index_1/self.numberOfColumns, index_1%self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND)

		for index_2, item in enumerate(self.labels[-7:-3], start = 1):
			b = bt.GenBitmapButton( self, -1, bitmap = self.labelBitmaps[item] )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetBezelWidth( 3 )
                        b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( (index_1+index_2)/self.numberOfColumns, (index_1+index_2)%self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND)

		for item in (self.labels[-3],):
			b = bt.GenButton( self, -1, item, name=item, size=(3*169, 150) )
			b.SetFont( wx.Font(35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetForegroundColour( self.textColor )
			b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( (index_1+index_2)/self.numberOfColumns, (index_1+index_2+1)%self.numberOfColumns ), (1, 3), wx.EXPAND)

		for index_3, item in enumerate(self.labels[-2:], start = 4):
			b = bt.GenBitmapButton( self, -1, bitmap = self.labelBitmaps[item] )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetBezelWidth( 3 )
                        b.Bind( wx.EVT_KEY_DOWN, self.onPress )

			self.sizer.Add(b, ( (index_1+index_2+index_3)/self.numberOfColumns, (index_1+index_2+index_3)%self.numberOfColumns), wx.DefaultSpan, wx.EXPAND)

		self.vbox.Add( self.sizer, proportion=1, flag=wx.EXPAND )
		self.SetSizer( self.vbox )
		self.Center()

	#-------------------------------------------------------------------------
	def initializeTimer(self):
		self.stoper = wx.Timer(self)
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper )
		self.stoper.Start( self.timeGap )
	
	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
	
	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):
		self.stoper.Stop()
		self.Destroy()

	#-------------------------------------------------------------------------
	def onExit(self):
		self.stoper.Stop()
		self.MakeModal( False )
		self.parent.Show()
		self.parent.stoper.Start( self.parent.timeGap )
		self.Destroy()
		
	#-------------------------------------------------------------------------
	def onPress(self, event):
        	keycode = event.GetKeyCode()
		if keycode == wx.WXK_SPACE and self.numberOfPresses == 0:
                	
			if self.flag == 'row':
				

				if self.rowIteration != self.numberOfRows:
					buttonsToHighlight = range( (self.rowIteration-1)*self.numberOfColumns, (self.rowIteration-1)*self.numberOfColumns + self.numberOfColumns )
				else:
					buttonsToHighlight = range( (self.rowIteration-1)*self.numberOfColumns, (self.rowIteration-1)*self.numberOfColumns + 6 )
			
				for button in buttonsToHighlight:
					item = self.sizer.GetItem( button )
					b = item.GetWindow()
					b.SetBackgroundColour( self.selectionColor )
					b.SetFocus()

				
				self.flag = 'columns' 
				self.rowIteration = self.rowIteration - 1
				self.colIteration = 0
				self.stoper.Start( self.timeGap )
			
			elif self.flag == 'columns' and self.rowIteration != self.numberOfRows-1:

				item = self.sizer.GetItem( (self.rowIteration)*self.numberOfColumns + self.colIteration-1 )
				b = item.GetWindow()
				b.SetBackgroundColour( self.selectionColor )
				b.SetFocus()

				label = self.labels[ self.rowIteration*self.numberOfColumns + self.colIteration-1 ]
				
				if label == 'SPECIAL_CHARACTERS':								
					self.stoper.Stop()
					specialCharacters( self, id=4 ).Show()
					
					message = self.textField.GetValue()
					Publisher().sendMessage( ( 'textFieldValue' ), message ) #call the Publisher object’s sendMessage method and pass it the topic string and the message in order to send the message
					
					self.Hide()

				else:
					mixer.init()
					mixer.Sound('./sounds/typewriter_key.wav').play()
					#self.typingSound.Play(wx.SOUND_SYNC)
					self.textField.AppendText( label )
				
				self.flag = 'row'
				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0
				self.stoper.Start( self.timeGap )

			elif self.flag == 'columns' and self.rowIteration == self.numberOfRows-1:
			
				item = self.sizer.GetItem( (self.rowIteration)*self.numberOfColumns + self.colIteration-1 )
				b = item.GetWindow()
				b.SetBackgroundColour( self.selectionColor )
				b.SetFocus()

				label = self.labels[ self.rowIteration*self.numberOfColumns + self.colIteration-1 ]
				
				if label == 'UNDO':						
					self.textField.Remove( self.textField.GetLastPosition()-1, self.textField.GetLastPosition() )
				
				elif label == 'SPEAK':								
					text = str( self.textField.GetValue() )
					
					inputTable = '~!#$&()[]{}<>;:"\|'
					outputTable = ' ' * len( inputTable )
					translateTable = maketrans( inputTable, outputTable )
					textToSpeech = text.translate( translateTable )

					replacements = { '-' : ' minus ' , '+' : ' plus ' , '*' : ' razy ' , '/' : ' podzielić na ' , '=' : ' równa się ' , '%' : ' procent ' }
					textToSpeech = reduce( lambda text, replacer: text.replace( *replacer ), replacements.iteritems(), textToSpeech )
										
					os.system( 'milena_say %s' %textToSpeech )
				
				elif label == 'SAVE' and self.textField.GetValue().replace( ' ', ',' ) != '':
					f=open( 'my_file.txt', 'w' )
                                        f.write( self.textField.GetValue() )
                                        f.close()

				elif label == 'SAVE' and self.textField.GetValue().replace( ' ', ',' ) == '':
					pass
				
				elif label == 'SPACJA':
					mixer.init()
					mixer.Sound('./sounds/typewriter_space.wav').play()
					self.textField.AppendText( ' ' )
				
				elif label == 'OPEN':
					textToLoad = open( 'myMessage.txt' ).read()
					self.textField.Clear()
					self.textField.AppendText( textToLoad )

	 			elif label == 'EXIT':
					self.onExit()			
				
				self.flag = 'row'
				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0
				self.stoper.Start( self.timeGap )

			self.numberOfPresses += 1

		else:
			event.Skip() #Event skip use in else statement here!			
	
	#-------------------------------------------------------------------------
	def timerUpdate(self, event):
		

		self.numberOfPresses = 0
		if self.flag == 'row':
		
			self.rowIteration = self.rowIteration % self.numberOfRows
			
			items = self.sizer.GetChildren()			
			for item in items:
				b = item.GetWindow()
				b.SetBackgroundColour( self.backgroundColor )
                                b.SetFocus()
			
			if self.rowIteration != self.numberOfRows-1:
				 buttonsToHighlight = range( self.rowIteration*self.numberOfColumns, self.rowIteration*self.numberOfColumns + self.numberOfColumns )
			else:
				buttonsToHighlight = range( self.rowIteration*self.numberOfColumns, self.rowIteration*self.numberOfColumns + 6 )
			
			for button in buttonsToHighlight:
				item = self.sizer.GetItem( button )
				b = item.GetWindow()
				b.SetBackgroundColour( self.scanningColor )
				b.SetFocus()

			self.rowIteration += 1
			
		elif self.flag == 'columns':

			if self.count == self.countMax:
				self.flag = 'row'

				item = self.sizer.GetItem( self.rowIteration*self.numberOfColumns + self.colIteration-1 )
				b = item.GetWindow()
				b.SetBackgroundColour( self.backgroundColor )

				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0


			else:
				if self.colIteration == self.numberOfColumns - 1 or ( self.colIteration == self.numberOfColumns-3 and self.rowIteration == self.numberOfRows-1 ):
					self.count += 1
				
				if self.colIteration == self.numberOfColumns or ( self.colIteration == self.numberOfColumns-2 and self.rowIteration == self.numberOfRows-1 ):
					self.colIteration = 0

				items = self.sizer.GetChildren()
				for item in items:
					b = item.GetWindow()
					b.SetBackgroundColour( self.backgroundColor )
                                        b.SetFocus()
				
				item = self.sizer.GetItem( self.rowIteration*self.numberOfColumns + self.colIteration )
				b = item.GetWindow()
				b.SetBackgroundColour( self.scanningColor )
				b.SetFocus()

				self.colIteration += 1
				
#=============================================================================
class specialCharacters(wx.Frame):
	def __init__(self, parent, id):

		wx.Frame.__init__( self , parent , id , 'ATPlatform Speller' )
		Publisher().subscribe( self.textFieldUpdate, ( 'textFieldValue' ) ) #connect to a signal called 'textFieldValue'

		self.Maximize( True )
		self.winWidth, self.winHight = self.GetSize()
		style = self.GetWindowStyle()
		self.SetWindowStyle( style | wx.STAY_ON_TOP )
		self.Centre()
		self.MakeModal( True )
		self.SetBackgroundColour( 'black' )
                self.parent = parent

		self.initializeParameters()			
		self.initializeBitmaps()
		self.createGui()								
		self.initializeTimer()					
		self.createBindings()						

	#-------------------------------------------------------------------------
	def initializeParameters(self):
		self.timeGap = 2000

		self.labels = '1 2 3 4 5 6 7 8 9 0 + - * / = % $ & . , ; : " ? ! @ # ( ) [ ] { } < > ~ UNDO SPEAK SAVE SPACJA OPEN EXIT'.split()

		self.flag = 'row'						
		self.numberOfRows = 5
		self.numberOfColumns = 9
		self.rowIteration = 0						
		self.colIteration = 0							
		self.count = 0										
		self.countMax = 2									
		self.numberOfPresses = 0
		
		self.backgroundColor = 'white'		
		self.textColor = 'black'
		self.selectionColor = '#D5FAFC' #DEDBDB'

	#-------------------------------------------------------------------------
        def initializeBitmaps(self):
            
            labelFiles = ['./icons/undo.png', './icons/speak.png', './icons/save.png', './icons/open.png', './icons/exit.png', ]
            
            self.labelBitmaps = {}
	    
	    labelBitmapIndex = [ self.labels.index( self.labels[-6] ), self.labels.index( self.labels[-5] ), self.labels.index( self.labels[-4] ), self.labels.index( self.labels[-2] ), self.labels.index( self.labels[-1]) ]

            for labelFilesIndex, labelIndex in enumerate( labelBitmapIndex ):
		    self.labelBitmaps[ self.labels[labelIndex] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[labelFilesIndex], 'rb' )) )			
	#-------------------------------------------------------------------------	
	def createGui(self):
		self.vbox = wx.BoxSizer( wx.VERTICAL )
		self.textField = wx.TextCtrl( self, style=wx.TE_LEFT, size=( self.winWidth, self.winHight - self.winWidth/1.1 ) )
		self.textField.SetFont( wx.Font(60, wx.SWISS, wx.NORMAL, wx.NORMAL) )
		self.vbox.Add( self.textField, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3 )
		self.sizer = wx.GridBagSizer(3, 3)

		for index_1, item in enumerate( self.labels[:-6] ):
			b = bt.GenButton( self, -1, item, name=item, size=(149,113) )
			b.SetFont( wx.Font(35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetForegroundColour( self.textColor )
			b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( index_1/self.numberOfColumns, index_1%self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND)

		for index_2, item in enumerate(self.labels[-6:-3], start = 1):
			b = bt.GenBitmapButton( self, -1, bitmap = self.labelBitmaps[item] )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetBezelWidth( 3 )
                        b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( (index_1+index_2)/self.numberOfColumns, (index_1+index_2)%self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND)

		for item in (self.labels[-3],):
			b = bt.GenButton( self, -1, item, name=item, size=(4*3*self.winWidth/self.numberOfColumns, 3*(self.winHight-self.winWidth/1.1)/self.numberOfRows) )
			b.SetFont( wx.Font(35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetForegroundColour( self.textColor )
			b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( (index_1+index_2)/self.numberOfColumns, (index_1+index_2+1)%self.numberOfColumns ), (1, 4), wx.EXPAND)

		for index_3, item in enumerate(self.labels[-2:], start = 5):
			b = bt.GenBitmapButton( self, -1, bitmap = self.labelBitmaps[item] )
			b.SetBackgroundColour( self.backgroundColor )
			b.SetBezelWidth( 3 )
                        b.Bind( wx.EVT_KEY_DOWN, self.onPress )
			self.sizer.Add(b, ( (index_1+index_2+index_3)/self.numberOfColumns, (index_1+index_2+index_3)%self.numberOfColumns), wx.DefaultSpan, wx.EXPAND)

		self.vbox.Add( self.sizer, proportion=1, flag=wx.EXPAND )
		self.SetSizer( self.vbox )
		self.Center()
	
	#-------------------------------------------------------------------------
	def textFieldUpdate(self, message):
		self.textField.SetValue(message.data)
	
	#-------------------------------------------------------------------------
	def initializeTimer(self):
		self.stoper = wx.Timer(self)
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper )
		self.stoper.Start( self.timeGap )
	
	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
	
	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):
		self.stoper.Stop()
		self.Destroy()

	#-------------------------------------------------------------------------
	def onExit(self):
		self.stoper.Stop()
		self.MakeModal( False )
		self.parent.Show()
		self.parent.stoper.Start( self.parent.timeGap )
		self.Destroy()
		
	#-------------------------------------------------------------------------
	def onPress(self, event):
        	keycode = event.GetKeyCode()
		if keycode == wx.WXK_SPACE and self.numberOfPresses == 0:
                	
			if self.flag == 'row':
				self.flag = 'columns' 
				self.rowIteration = self.rowIteration - 1
				self.colIteration = 0
				self.stoper.Start( self.timeGap )
			
			elif self.flag == 'columns' and self.rowIteration != self.numberOfRows-1:
				item = self.sizer.GetItem( self.rowIteration*self.numberOfColumns + self.colIteration - 1 )
				b = item.GetWindow()
				label = b.GetLabel()
				
				self.textField.AppendText( label )
				self.parent.textField.AppendText( label )

				self.flag = 'row'
				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0
				self.stoper.Start( self.timeGap )

			elif self.flag == 'columns' and self.rowIteration == self.numberOfRows-1:
				label = self.labels[ self.rowIteration*self.numberOfColumns + self.colIteration-1 ]
				
				if label == 'UNDO':						
					self.textField.Remove( self.textField.GetLastPosition()-1, self.textField.GetLastPosition() )
					self.textField.Remove( self.parent.textField.GetLastPosition()-1, self.parent.textField.GetLastPosition() )
				
				elif label == 'SPEAK':
					text = str(self.textField.GetValue())
					
					inputTable = '~!#$&()[]{}<>;:"\|'
					outputTable = ' ' * len( inputTable )
					translateTable = maketrans( inputTable, outputTable )
					textToSpeech = text.translate( translateTable )

					replacements = { '-' : ' minus ' , '+' : ' plus ' , '*' : ' razy ' , '/' : ' podzielić na ' , '=' : ' równa się ' , '%' : ' procent ' }
					textToSpeech = reduce( lambda text, replacer: text.replace( *replacer ), replacements.iteritems(), textToSpeech )
										
					os.system( 'milena_say %s' %textToSpeech )
								
				elif label == 'SAVE' and self.textField.GetValue().replace( ' ', ',' ) != '':
					textToSave = open( 'myMessage.txt', 'w' )
                                        textToSave.write( self.textField.GetValue() )
                                        textToSave.close()

				elif label == 'SAVE' and self.textField.GetValue().replace( ' ', ',' ) == '':
					pass
				
				elif label == 'SPACJA':

					self.textField.AppendText( ' ' )
				
				elif label == 'OPEN':
					textToLoad = open( 'myMessage.txt' ).read()
					self.textField.Clear()
					self.textField.AppendText( textToLoad )

	 			elif label == 'EXIT':
					self.onExit()			
				
				self.flag = 'row'
				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0
				self.stoper.Start( self.timeGap )
			
			self.numberOfPresses += 1

		else:
			event.Skip() #Event skip use in else statement here!			
	
	#-------------------------------------------------------------------------
	def timerUpdate(self, event):
		
		self.numberOfPresses = 0
		if self.flag == 'row':

			self.rowIteration = self.rowIteration % self.numberOfRows

			items = self.sizer.GetChildren()			
			for item in items:
				b = item.GetWindow()
				b.SetBackgroundColour( self.backgroundColor )
                                b.SetFocus()
			
			if self.rowIteration != self.numberOfRows-1:
				 buttonsToHighlight = range( self.rowIteration*self.numberOfColumns, self.rowIteration*self.numberOfColumns + self.numberOfColumns )
			else:
				buttonsToHighlight = range( self.rowIteration*self.numberOfColumns, self.rowIteration*self.numberOfColumns + 6 )
			
			for button in buttonsToHighlight:
				item = self.sizer.GetItem( button )
				b = item.GetWindow()
				b.SetBackgroundColour( self.selectionColor )
				b.SetFocus()

			self.rowIteration += 1
			
		elif self.flag == 'columns':

			if self.count == self.countMax:
				self.flag = 'row'
				self.rowIteration = 0
				self.colIteration = 0
				self.count = 0
			else:
				if self.colIteration == self.numberOfColumns or ( self.rowIteration == self.numberOfRows-1 and self.colIteration == 6 ):
					self.colIteration = 0
					self.count += 1
			
				items = self.sizer.GetChildren()
				for item in items:
					b = item.GetWindow()
					b.SetBackgroundColour( self.backgroundColor )
                                        b.SetFocus()
				
				item = self.sizer.GetItem( self.rowIteration*self.numberOfColumns + self.colIteration )
				b = item.GetWindow()
				b.SetBackgroundColour( self.selectionColor )
				b.SetFocus()

				self.colIteration += 1

#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp()
	frame = speller( parent = None, id = -1 )
	frame.Show()
	app.MainLoop()
