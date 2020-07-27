# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
#SLave address+Func.code+Reg_addr(2B)+number of Words(2B)+CRC(2B) = 8 B

Slave_add = 0x01
def Modbus_RTU_MasterMsg_parse(msg):
    global Slave_add
    ret = None
    CRC = None
    CRC_Lo = None
    CRC_Hi = None
    # 3 to read NUID 4Bytes data
    # 4 to read user date, assume 8 Bytes?
    # 1 slave address not match
    # 0 unvalid msg,(length  error)
    # -1 errors
    # -2 error with CRC
    # 
    msg_len = len(msg)
    if (msg_len!=8):
        ret = 0
        print("#>:Modbus Msg lengh not equal to 8!")
        return ret
    else:
        CRC = calc_crc(msg[0:-2])
        CRC_Hi = CRC>>8
        CRC_Lo = CRC&0x00FF
        print("#>:Calc CRC:")
        print(str(hex(CRC)))
        #print(str(hex(CRC_Hi)))
        #print(str(hex(CRC_Lo)))
        CRC_Ori = msg[-2]+msg[-1]<<8
        CRC_Ori = msg[-1]<<8
        CRC_Ori +=  msg[-2]
        print("RX CRC: "+(hex(CRC_Ori)))
        print(hex(msg[-1]))
        print(hex(msg[-2]))
        if (CRC!= CRC_Ori):
            ret = -2
            print("#>:Modbus Msg CRC error!")
            return ret
        
    if (msg[0] == Slave_add):
        ret =  msg[1]
        if (ret>5):
            ret = -1
        elif(ret<1):
            ret = -1
        print("Modbus Master Msg parse successful!")
        return ret
    else:
        ret =1
        #print("#>:Modbus slave address not match!")
        return ret
        
def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos 
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

print("Hello world")
tmp_msg = bytearray(8)#
tmp_msg[0] = 0x01
tmp_msg[1] = 0x03
tmp_msg[2] = 0x00
tmp_msg[3] = 0x00
tmp_msg[4] = 0x00
tmp_msg[5] = 0x01
#CRC_bytes = tmp_msg[0:5]
CRC_list= list (tmp_msg[0:-2])
CRC_Res= calc_crc(CRC_list)
tmp_msg[6] = CRC_Res&0x00FF
tmp_msg[7] = CRC_Res>>8
print(tmp_msg)
print(hex(CRC_Res))#0xc212
res = Modbus_RTU_MasterMsg_parse(tmp_msg)
#0xcf45
print("msg parse result")
print(res)
RFID_ID_pre = 0x5b
tmp_var = int(RFID_ID_pre)
print(tmp_var)

tmp_msg2 = bytearray(7)#
tmp_msg2[0] = 0x01
tmp_msg2[1] = 0x03
tmp_msg2[2] = 0x04
tmp_msg2[3] = 0x6b
tmp_msg2[4] = 0x12
tmp_msg2[5] = 0x5d
tmp_msg2[6] = 0xa6
CRC_list2= list(tmp_msg2)
CRC_Res2= calc_crc(CRC_list2)
print(tmp_msg2)
print(hex(CRC_Res2))
#print(str(CRC_list2[0:3])+hex(CRC_list2[3])+hex(CRC_list2[4])+hex(CRC_list2[5])+hex(CRC_list2[6]))
print(str(CRC_list2[0:3])+"+["+str(f'{CRC_list2[3]:x}')+str(f'{CRC_list2[4]:x}')+str(f'{CRC_list2[5]:x}')+str(f'{CRC_list2[6]:x}')+"]")
print(str(CRC_list2[0:3])+"+["+str(f'{CRC_list2[3]:x}')+str(f'{CRC_list2[4]:x}')+str(f'{CRC_list2[5]:x}')+str(f'{CRC_list2[6]:x}')+"]+["+hex(CRC_Res2)+"]")
#print(f'{14:x}')
payload=tmp_msg+tmp_msg2
#print(payload)
#5FDA
#6b125da6
