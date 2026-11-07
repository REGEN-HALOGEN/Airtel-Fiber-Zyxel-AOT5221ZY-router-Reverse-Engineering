#!/bin/sh

echo RULE 0 SIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter
echo 0xb79 > /proc/fc/trace/filter_level
echo 0xb79 > /proc/fc/trace/debug_level
echo RULE 0 SIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter

echo RULE 0 SIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo 0x1f > /proc/rtk_smuxdev/debug
echo RULE 0 SIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.4.1 91.108.7.254 TIMES 20 > /proc/rtk_smuxdev/filter


echo RULE 0 SIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter
echo 0xb79 > /proc/fc/trace/filter_level
echo 0xb79 > /proc/fc/trace/debug_level
echo RULE 0 SIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter

echo RULE 0 SIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo 0x1f > /proc/rtk_smuxdev/debug
echo RULE 0 SIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.56.1 91.108.59.254 TIMES 20 > /proc/rtk_smuxdev/filter


echo RULE 0 SIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter
echo 0xb79 > /proc/fc/trace/filter_level
echo 0xb79 > /proc/fc/trace/debug_level
echo RULE 0 SIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter

echo RULE 0 SIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo 0x1f > /proc/rtk_smuxdev/debug
echo RULE 0 SIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 91.108.8.1 91.108.11.254 TIMES 20 > /proc/rtk_smuxdev/filter


echo RULE 0 SIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter
echo 0xb79 > /proc/fc/trace/filter_level
echo 0xb79 > /proc/fc/trace/debug_level
echo RULE 0 SIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter

echo RULE 0 SIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo 0x1f > /proc/rtk_smuxdev/debug
echo RULE 0 SIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 95.161.64.1 95.161.79.254 TIMES 20 > /proc/rtk_smuxdev/filter


echo RULE 0 SIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter
echo 0xb79 > /proc/fc/trace/filter_level
echo 0xb79 > /proc/fc/trace/debug_level
echo RULE 0 SIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/fc/trace/trace_filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254 TIMES 20 > /proc/fc/trace/trace_filter

echo RULE 0 SIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo 0x1f > /proc/rtk_smuxdev/debug
echo RULE 0 SIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/rtk_smuxdev/filter
echo RULE 1 SIP_RANGE 192.168.1.2 192.168.1.254  DIP_RANGE 149.154.160.1 149.154.167.254 TIMES 20 > /proc/rtk_smuxdev/filter

sleep 3;
