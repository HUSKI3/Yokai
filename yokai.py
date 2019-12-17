import os

def intro():
  print(''' __     __   _  __     _ 
 \ \   / /  | |/ /    (_)
  \ \_/ /__ | ' / __ _ _ 
   \   / _ \|  < / _` | |
    | | (_) | . \ (_| | |
    |_|\___/|_|\_\__,_|_|
                         
                         ''')
  print(" By Linkus")
  print("WARNING - This script only works on Linux and Unix based systems, see README.txt for more info...")


def create_kernel_asm(nm):
  print("[YoKai] Starting 32bit Kernel Build")
  print("[YoKai] Kernel.asm building...")
  asm = open("os.asm","w+")
  asm.write('''[bits 16]
[org 0x7c00]

bootloader_entry:
  xor ax,ax
  mov ds,ax
  mov es,ax

  mov ah, 0x02
  mov al, 0x10
  mov dl, 0x80
  mov ch, 0
  mov dh, 0
  mov cl, 2
  mov bx, kernel_entry
  int 0x13

  cli
  cld

  jmp kernel_entry

  times (510 - ($ - $$)) db 0x00
  dw 0xAA55


kernel_entry:

  call disable_cursor

  call load_vga

  ; clear screen with black background and white foreground
  ; colors
  ;0x0  black
  ;0x1	blue
  ;0x2  green
  ;0x3  cyan
  ;0x4  red
  ;0x5	magenta
  ;0x6  brown
  ;0x7  gray
  ;0x8  dark gray
  ;0x9  bright blue
  ;0xA  bright green
  ;0xB  bright cyan
  ;0xC  bright red
  ;0xD  bright magenta
  ;0xE  yellow
  ;0xF  white
  mov byte[VGA_FORE_COLOR], 0xF
  mov byte[VGA_BACK_COLOR], 0x7
  call clear_screen



  ; increase VGA_INDEX to some 2 bytes amount
  ; so that it could lead to center of the screen
  add word[VGA_INDEX], 1824

  mov si, msg_str
  call print_string
  mov si, message_str
  call print_string


  hlt
  ret


print_string:

.char_loop :
	lodsb

	cmp al, 0
	je .exit

  mov byte[VGA_CHAR], al
  call vga_print_char

  add word[VGA_INDEX], 2

  jmp .char_loop

.exit:
	ret


disable_cursor:
  mov ah, 0x01
  mov ch, 1
  mov cl, 0
  int 0x10
  ret


load_vga:
  ; get vga memory address and point set es to it
  mov dx, [VGA_ADDRESS]
  mov es, dx
  ret


vga_print_char:
  mov di, word[VGA_INDEX]
  mov al, byte[VGA_CHAR]

  ; 1 byte fore and back color
  ; high 4 bits : back color
  ; low 4 bits : fore color

  ; get back color
  mov ah, byte[VGA_BACK_COLOR]
  ; rotate it by 4 to left,
  ; for high 4 bits
  sal ah, 4
  ; oring with fore color value
  or ah, byte[VGA_FORE_COLOR]

  ; see kernel.c source, from Kernel folder

  mov [es:di], ax

  ret


; clear screen just displays null characters
clear_screen:
  ;set index to 0
  mov di, 0

.clrloop:
  cmp di, word[MAX_VGA_INDEX]
  jg .exit

  ; get null character into al
  mov al, 0

  mov ah, byte[VGA_BACK_COLOR]
  sal ah, 4
  or ah, byte[VGA_FORE_COLOR]

  ; put value of al into vga memory address
  mov [es:di], ax

  ; increase di by 2 (2 bytes)
  add di, 2
  jmp .clrloop

.exit:
  mov word[VGA_INDEX], 0
  ret


  times (4096 - ($ - $$)) db 0x00

section .data
  VGA_ADDRESS dw 0xB800
  MAX_VGA_INDEX dw 0xF9E    ; 3998 in decimal
  VGA_INDEX dw 0
  VGA_CHAR db 0
  VGA_FORE_COLOR db 0xF
  VGA_BACK_COLOR db 0x0

section .rodata
  msg_str db '{name}', 0
  message_str db ' Version: 0.0.0', 0
'''.format(name=nm))


#
##EXPERIMENTAL_________________________
#
#def create_kernel_c():
#  print("[YoKai] Kernel.c building...")
#  c = open("kernel.c","w+")
#  c.write('''kmain()
#{
#        char* vidmem=(char*)0xb8000;
#        vidmem[0] = 'A';
#        vidmem[1] = 0x02;
#}
#''')
#  c.close()
#  print("[YoKai] Kernel.c build [OK]")
#
#def create_link_ld():
#  print("[YoKai] Link.ld building...")
#  ld = open("link.ld","w+")
#  ld.write('''OUTPUT_FORMAT(elf32-i386)
#ENTRY(start)
#SECTIONS
# {
#   . = 0x100000;
#   .text : { *(.text) }
#   .data : { *(.data) }
#   .bss  : { *(.bss)  }
# }
#''')
#  ld.close()
#  print("[YoKai] Kernel.c build [OK]")
#########################################
#
#

def main():
  intro()
  name = input("[YoKai] Name of your OS: ")
  create_kernel_asm(name)
  print("[YoKai] Kernel.asm build [OK]")
  #create_kernel_c()
  #create_link_ld()
  print("[YoKai] Build Complete!")
  while True:
    x = input("[YoKai] Compile and run? [y/n]")
    if x == "y":
      os.system("nasm -f bin os.asm -o os.bin")
      os.system("qemu-system-x86_64 os.bin")
      break
    else:
      print("[YoKai] The files are in the same directory as this script")
      break


main()