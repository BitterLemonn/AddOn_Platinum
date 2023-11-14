# -*- coding: utf-8 -*-
class ViewBinder(object):
	ButtonFilter = 0x10000000
	BF_ButtonClickUp	=	0 | ButtonFilter
	BF_ButtonClickDown	=	1 | ButtonFilter
	BF_ButtonClick		= 	2 | ButtonFilter
	BF_ButtonClickCancel= 	3
	BF_InteractButtonClick = 4
	BindFilter = 0x01000000
	BF_BindBool		= 5 | BindFilter
	BF_BindInt		= 6 | BindFilter
	BF_BindFloat	= 7 | BindFilter
	BF_BindString	= 8 | BindFilter
	BF_BindGridSize = 9 | BindFilter
	BF_BindColor	= 10 | BindFilter
	EditFilter = 0x00100000
	BF_EditChanged	= 11 | EditFilter
	BF_EditFinished	= 12 | EditFilter
	ToggleFilter = 0x00010000
	BF_ToggleChanged = 13 | ToggleFilter
	SliderFilter = 0x00001000
	BF_SliderChanged = 14 | SliderFilter
	BF_SliderFinished = 15 | SliderFilter

	@staticmethod
	def binding(bind_flag, binding_name = None):
		pass

	@staticmethod
	def binding_collection(bind_flag, collection_name, binding_name = None):
		pass

