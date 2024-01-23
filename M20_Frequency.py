#!/usr/bin/env python
# -*- coding:Utf8 -*-
# m20_434MHz.py
# version 15/11/2022
# Original code from https://keraman.free.fr/m20/m20.html

import os

# Function to choose the name and frequency
def choose_parameters():
    name = input("Enter the file name: ")
    frequency = int(input("Enter the frequency in kHz: "))
    return name, frequency

''' 
You must also dismiss a few turns of the self-induction at the pins 15 and 16 of the circuit ADF7012
to get a voltage between 0.5V and 2.2V at the pin VCO 18
'''

# By default, let the user pick the name and frequency
name, frequency = choose_parameters()

debug = True
printx = False
s = name.split('.')
nomD = '%s_%d.%s' % (s[0], frequency, s[1])
print('file src =', name)
print('file dest=', nomD)

tab = (
    # delete function division
    (0xb52, 0x17, 0x48, 'ldr r0,[DAT_80000bb0]', 0x00, 0xbf, "nop"),  # suppress crash due to forbidden memory access
    (0xb54, 0x0a, 0x21, 'movs r1,#0xa', 0x00, 0xbf, "nop"),
    (0xb56, 0x00, 0x78, 'ldrb r0,[r0,#0x0]=>DAT_000ca001', 0x00, 0xbf, "nop"),
    (0xb58, 0xc0, 0x02, 'lsls r0,r0,#0xb', 0x00, 0xbf, "nop"),
    (0xb5a, 0xff, 0xf7, 'bl uint32_div_with_rem', 0x00, 0xbf, "nop"),
    (0xb5c, 0xc9, 0xfa, 'bl uint32_div_with_rem', 0x00, 0xbf, "nop"),

    # reg 0
    # (0xb7e,0x00,0x88,'ldrh r0,[r0,#0x0]=>DAT_2000009c',0x0e,0x48,'ldr r0,[DAT_0xbb8]'),# 8 --> a
    # (0xb80,0x08,0x80,'strh r0,[r1,#0x0]=>local_18',0x00,0x90,'str r0,[sp,#0x0]=>Data'),

    # reg 1 frequency
    (0xb88, 0x0c, 0x20, "movs r0,#0xc", 0x00, 0xbf, "nop"),
    (0xb8a, 0x69, 0x46, "mov  r1,sp", 0x00, 0xbf, "nop"),
    (0xb8c, 0x48, 0x80, "strh r0,[r1,#Data+0x2]", 0x08, 0x48, "ldr r0,[PTR_DAT_0xbb0]"),
    (0xb8e, 0x0d, 0x80, "strh r5,[r1,#0x0]=>Data", 0x00, 0x90, "str r0,[sp,#0x0]=>Data"))

tbReg1 = (0xbb0, 0x18, 0x00, 0x08, 0x08, '---> reg1=', 0x01, 0xA0, 0x0C, 0x00, 0x000cA001, '404MHz')

if debug:
    # test address PTR_DATA
    adr1 = tab[0][0] & 0xfffffffC
    adr2 = tbReg1[0]
    offsetPC = tab[0][1] + 1
    print('adr1=%s adr2=%s delta=%d offset=%d' % (hex(adr1), hex(adr2), (adr2 - adr1) / 4, offsetPC))

# calculate frequency
reg1 = (round(frequency * 0xca000 / 404000) & 0xfffffffC) + 1
print('reg1=', hex(reg1))

def printError(adr, av, ap):
    print('data not compatible %s %s # %s' % (adr, av, ap))

def hexa(n):
    return format(n, '02x')

error = False
f = open(name, "rb")
length = os.path.getsize(name)
print('file length=', length)

def address(x):
    return x + offset

n = 0
dest = []
try:
    file_content = f.read(length)
    na = 0
    err = True
    for c in file_content:  # find: e2 5f and af 18 for ADF7012_initialize 0x8000b50
        n = n + 1
        if c == 0xe2:
            na = n + 1
        if c == 0x5f and na == n:
            if debug:
                print('ok adr "e2 5f"=', hex(n - 2))
            offset = (n - 2) - 0xbbc
            err = False
        dest.append(c)
    if err:
        print('not find 0xe2 0x5 , file ' + name + ' not compatible')
        error = True
    else:
        error = err
        for el in tab:
            adr = address(el[0])
            adrs = hex(adr + 0x08000000)
            s1 = hexa(el[1])
            if (dest[adr] == el[1]) or (el[3][:3] == 'bl '):  # the address of the division function can vary
                dest[adr] = el[4]
                d1 = hexa(el[4])
            else:
                printError(adrs, hexa(dest[adr]), s1)
                error = True
            if (dest[adr + 1] == el[2]) or (el[3][:3] == 'bl '):  # the address of the division function can vary
                dest[adr + 1] = el[5]
                if printx:
                    s1 = s1 + ' ' + hexa(el[2])
                    d1 = d1 + ' ' + hexa(el[5])
                    print('%s %s--> %s' % (adrs, s1, d1))
            else:
                adrs = hex(adr + 0x08000001)
                printError(adrs, hexa(dest[adr + 1]), hexa(el[2]))
                error = True
        ds = ''
        s1 = ''
        for i in range(4):
            adr = address(tbReg1[0])
            if dest[adr + i] == tbReg1[1 + i]:
                byte = reg1 & 0xff
                reg1 = reg1 >> 8
                dest[adr + i] = byte
                s1 = s1 + ' ' + hexa(tbReg1[1 + i])
                ds = ds + ' ' + hexa(byte)
            else:
                printError(hex(adr + i + 0x08000000), hex(dest[adr + i]), hex(tbReg1[1 + i]))
                error = True
        if printx:
            adrs = hex(adr + 0x08000000)
            print('%s %s--> %s' % (adrs, s1, ds))
        print('for Frequency %dkHz reg1=%s' % (frequency, ds))

except IOError:
    # Your error handling here
    # Nothing for this example
    pass
finally:
    f.close()

if not error:
    fd = open(nomD, "wb")
    x = bytearray(dest)
    fd.write(x)
    fd.close()
    print('write file --->', nomD)
