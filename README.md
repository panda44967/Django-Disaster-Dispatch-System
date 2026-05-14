# rescue_center — 城市災害應變與物資調度平台

學號：**P1146106**  

**建議目錄結構**

- `midterm_P1146106/`：繳交壓縮檔解壓後的最外層資料夾  
- `midterm_P1146106/P1146106/`：本機虛擬環境（**繳交時刪除**，勿打包進 zip）  
- `midterm_P1146106/rescue_center/`：**Django 專案根目錄**（本 README、`manage.py`、`db.sqlite3`、`requirements.txt` 所在層）  

Django：**5.0.0**  
自訂 app：`operations`

## 虛擬環境（繳交時請勿包含資料夾）

於最外層 `midterm_P1146106` 下建立名為 **`P1146106`** 的虛擬環境，啟用後進入 **`rescue_center`** 再安裝依賴：

```bash
cd midterm_P1146106
python -m venv P1146106
P1146106\Scripts\activate
cd rescue_center
pip install -r requirements.txt
```

以下所有 `python manage.py …` 指令皆請在 **`rescue_center`** 目錄內執行。

## 初次建立資料庫與使用者

```bash
python manage.py migrate
python manage.py seed_users
```

- 管理者：`ntub` / `123`（可登入 `/admin/`）
- 一般使用者（程式建立）：`cmd_center_01`、`medical_01`、`logistics_01`、`shelter_01`（預設密碼 `pass12345`），並具備 `ResponderProfile` 角色資料。

### 示範事件資料（選用，還原助教驗收用 db）

若需快速建立與繳交檔一致的示範 **Incident / ResourceRequest / ActionLog**（仍符合「通報者、提出者、執行者分散在不同 User」之關聯），在 `seed_users` 之後執行：

```bash
python manage.py seed_demo_data
```

正式作答流程仍建議：先 `seed_users`，再於 **Django Admin** 手動建立事件與關聯資料。

## Migration 流程紀錄（依考題要求）

已執行：

```bash
python manage.py makemigrations operations
python manage.py sqlmigrate operations 0001
python manage.py migrate
python manage.py showmigrations operations
```

### `showmigrations operations` 結果

```
operations
 [X] 0001_initial
```

### `sqlmigrate operations 0001` 部分輸出

```
BEGIN;
--
-- Create model Incident
--
CREATE TABLE "operations_incident" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "category" varchar(50) NOT NULL, "priority" integer NOT NULL, "location" varchar(200) NOT NULL, "description" text NOT NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "reporter_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ActionLog
--
CREATE TABLE "operations_actionlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "note" text NOT NULL, "created_at" datetime NOT NULL, "actor_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "incident_id" bigint NOT NULL REFERENCES "operations_incident" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ResourceRequest
--
CREATE TABLE "operations_resourcerequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "item_name" varchar(200) NOT NULL, "quantity" integer NOT NULL, "status" varchar(20) NOT NULL, "is_urgent" bool NOT NULL, "incident_id" bigint NOT NULL REFERENCES "operations_incident" ("id") DEFERRABLE INITIALLY DEFERRED, "requested_by_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ResponderProfile
--
CREATE TABLE "operations_responderprofile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "role" varchar(20) NOT NULL, "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
...
COMMIT;
```

## 建立的 Model 名稱

1. `Incident` — 災害／緊急事件  
2. `ResourceRequest` — 物資需求  
3. `ActionLog` — 處置紀錄  
4. `ResponderProfile` — 一般使用者角色（符合題目「角色可由資料庫查詢」之實作）

## 目前 `db.sqlite3` 資料筆數（示範環境）

| 資料表概念 | 筆數 |
|------------|------|
| `auth_user`（含 1 管理者 + 4 一般使用者） | 5 |
| `ResponderProfile` | 4 |
| `Incident` | 4 |
| `ResourceRequest` | 8 |
| `ActionLog` | 8 |

## 執行測試

```bash
python manage.py test operations
```

## 主要前台路徑

| 路徑 | 說明 |
|------|------|
| `/` | 首頁（所有 Incident，`ListView`） |
| `/incidents/search/` | 事件查詢（GET 表單） |
| `/guide/` | 應變指引（`TemplateView` + 巢狀 context） |
| `/responders/` | 人員名冊（一般使用者 + 角色） |
| `/stats/` | 統計頁 |
| `/incident/new/` | 新增事件 |
| `/incident/<pk>/` | 事件詳細 |
| `/incident/<pk>/edit/` | 修改事件（標題凍結） |
| `/incident/<pk>/delete/` | 刪除確認 |

首頁網址為 `/`，瀏覽根路徑即進入災害應變首頁。
