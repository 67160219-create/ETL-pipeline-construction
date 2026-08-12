# วิธีรัน WEEK06 (Windows PowerShell)

เปิด PowerShell ที่โฟลเดอร์ `week06` แล้วรัน:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.main
python -m src.main
```

ถ้า PowerShell ไม่อนุญาตให้ activate ให้รันคำสั่งนี้เฉพาะหน้าต่างปัจจุบันก่อน:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

ตรวจผลลัพธ์:

```powershell
Get-Content .\output\validation.json
Get-Content .\output\rejects.csv
Get-Content .\logs\etl.log
```

ค่าที่ควรได้จากข้อมูลชุดนี้:

- `source_valid_rows`: 100
- `warehouse_rows`: 100
- `duplicate_order_ids`: 0
- `source_total_sales`: 192074.66
- `warehouse_total_sales`: 192074.66
- `status`: `PASS`
- จำนวน reject: 4

การรันครั้งที่สองต้องยังคงมีข้อมูลใน `fact_sales` 100 แถว เพราะ `order_id` เป็น Primary Key และใช้ `INSERT OR IGNORE`.
