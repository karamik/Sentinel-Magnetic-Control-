# ==============================================================================
# SMC v10.2: Automated Hardware Flashing Script
# (c) 2026 International Group of Developers / TOTAL Protocol Foundation
# ==============================================================================

# Настройки целевой платформы (Xilinx ZCU111)
set bitstream_path "./SMC_v10_2_eval.bit"
set device_pattern "xczu11eg*"

puts "=== TOTAL SMC v10.2: Starting Hardware Flashing Tool ==="

# 1. Открываем менеджер оборудования Vivado
open_hw_manager

# 2. Подключаемся к локальному серверу отладки (куда плата подключена по USB/JTAG)
connect_hw_server -url localhost:3121 -allow_non_jtag
puts "Connecting to local hardware server..."
refresh_hw_server

# 3. Находим целевую плату
set target_found 0
foreach hw_target [get_hw_targets] {
    open_hw_target $hw_target
    set hw_devices [get_hw_devices]
    
    foreach hw_device $hw_devices {
        if {[string match $device_pattern $hw_device]} {
            puts "Found Target Device: $hw_device"
            current_hw_device $hw_device
            set target_found 1
            break
        }
    }
    if {$target_found} { break }
    close_hw_target
}

if {!$target_found} {
    puts "ERROR: Target Xilinx ZCU111 board (xczu11eg) not found. Check JTAG/USB cable."
    exit 1
}

# 4. Задаем путь к файлу прошивки и заливаем его в память ПЛИС
puts "Loading evaluation bitstream: $bitstream_path"
set_property PROGRAM.FILE $bitstream_path [current_hw_device]

puts "Flashing FPGA logic... Please wait..."
program_hw_device [current_hw_device]

# 5. Проверяем статус и закрываем сессию
refresh_hw_device [current_hw_device]
puts "=== SUCCESS: SMC v10.2 Core Loaded Successfully ==="
puts "Notice: 4-hour evaluation window has started."

close_hw_manager
exit 0
