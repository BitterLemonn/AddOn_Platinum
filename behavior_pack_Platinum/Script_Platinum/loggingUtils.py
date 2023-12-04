# coding=utf-8
import logging
import re


def cut_text(text, length):
    textArr = re.findall('.{' + str(length) + '}', text)
    textArr.append(text[(len(textArr) * length):])
    return textArr


def info(infoMsg):
    formattedList = []
    if len(infoMsg) <= 20:
        formattedList.append(infoMsg)
    else:
        formattedList = cut_text(infoMsg, 300)

    print "===================="
    for i in formattedList:
        print i
    print "===================="


def infoLines(infoList):
    logging.info("====================")
    for i in infoList:
        logging.info(i)
    logging.info("====================")


def warn(warnMsg):
    formattedList = []
    if len(warnMsg) <= 20:
        formattedList.append(warnMsg)
    else:
        formattedList = cut_text(warnMsg, 300)
    logging.warn("====================")
    for i in formattedList:
        logging.warn(i)
    logging.warn("====================")


def error(errMsg):
    formattedList = []
    if len(errMsg) <= 20:
        formattedList.append(errMsg)
    else:
        formattedList = cut_text(errMsg, 300)
    logging.error("====================")
    for i in formattedList:
        logging.error(i)
    logging.error("====================")
