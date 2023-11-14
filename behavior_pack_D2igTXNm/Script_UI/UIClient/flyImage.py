# -*- coding: utf-8 -*-

from CustomFurnaceScripts.modCommon import modConfig


class FlyImage(object):
    def __init__(self, path):
        super(FlyImage, self).__init__()
        self.mPath = path
        self.mToPosition = []
        self.mFromPosition = []
        self.mCurPosition = []
        self.mDeltaX = 0
        self.mDeltaY = 0
        self.mIsUsing = False

    def InitPosition(self, fromPosition, toPosition):
        self.mFromPosition = fromPosition
        self.mToPosition = toPosition
        self.mCurPosition = list(fromPosition)
        self.mIsUsing = True
        self.mDeltaX = (self.mToPosition[0] - self.mFromPosition[0]) * 1.0 / modConfig.FLY_ANIMATION_DURATION
        self.mDeltaY = (self.mToPosition[1] - self.mFromPosition[1]) * 1.0 / modConfig.FLY_ANIMATION_DURATION

    def UpdateCurPosition(self):
        self.mCurPosition[0] += self.mDeltaX
        self.mCurPosition[1] += self.mDeltaY
        return tuple(self.mCurPosition)

    def IsUsing(self):
        return self.mIsUsing

    def Release(self):
        self.mIsUsing = False

    def GetPath(self):
        return self.mPath
