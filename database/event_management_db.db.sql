BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS Admins (
    admin_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    role       TEXT,
    status     TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    UNIQUE (college_id, email),
    FOREIGN KEY (college_id) REFERENCES Colleges(college_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL UNIQUE,
    attended        INTEGER NOT NULL DEFAULT 0 CHECK (attended IN (0,1)),
    check_in_time   TEXT,
    FOREIGN KEY (registration_id) REFERENCES Registrations(registration_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS AuditLogs (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    action      TEXT NOT NULL,
    table_name  TEXT NOT NULL,
    record_id   INTEGER,
    old_data    TEXT,
    new_data    TEXT,
    changed_at  TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS Colleges (
    college_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    location   TEXT,
    status     TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive'))
);
CREATE TABLE IF NOT EXISTS EventTypes (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS Events (
    event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id  INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    type_id     INTEGER NOT NULL,
    venue       TEXT,
    start_time  TEXT NOT NULL,
    end_time    TEXT NOT NULL,
    capacity    INTEGER NOT NULL CHECK (capacity >= 0),
    created_by  INTEGER NOT NULL,
    semester    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','cancelled','completed')),
    FOREIGN KEY (college_id) REFERENCES Colleges(college_id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES Admins(admin_id) ON DELETE RESTRICT,
    FOREIGN KEY (type_id) REFERENCES EventTypes(type_id),
    CHECK (julianday(end_time) > julianday(start_time))
);
CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id INTEGER NOT NULL UNIQUE,
    rating          INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments        TEXT,
    submitted_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (registration_id) REFERENCES Registrations(registration_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS Registrations (
    registration_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id        INTEGER NOT NULL,
    event_id          INTEGER NOT NULL,
    registration_time TEXT NOT NULL DEFAULT (datetime('now')),
    status            TEXT NOT NULL DEFAULT 'registered' CHECK (status IN ('registered','cancelled')),
    UNIQUE (student_id, event_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE RESTRICT,
    FOREIGN KEY (event_id)   REFERENCES Events(event_id)   ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    department TEXT,
    year       TEXT,
    status     TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    UNIQUE (college_id, email),
    FOREIGN KEY (college_id) REFERENCES Colleges(college_id) ON DELETE RESTRICT
);
INSERT INTO "EventTypes" ("type_id","name") VALUES (1,'Workshop'),
 (2,'Hackathon'),
 (3,'Fest'),
 (4,'Seminar'),
 (5,'Talk'),
 (6,'Other');
CREATE INDEX idx_attendance_reg        ON Attendance(registration_id);
CREATE INDEX idx_events_college        ON Events(college_id);
CREATE INDEX idx_events_semester       ON Events(semester);
CREATE INDEX idx_events_status         ON Events(status);
CREATE INDEX idx_events_type           ON Events(type_id);
CREATE INDEX idx_feedback_reg          ON Feedback(registration_id);
CREATE INDEX idx_registrations_event   ON Registrations(event_id);
CREATE INDEX idx_registrations_student ON Registrations(student_id);
CREATE INDEX idx_students_college      ON Students(college_id);
CREATE TRIGGER trg_audit_delete
AFTER DELETE ON Events
FOR EACH ROW
BEGIN
  INSERT INTO AuditLogs(action, table_name, record_id, old_data)
  VALUES('DELETE','Events',OLD.event_id,OLD.title);
END;
CREATE TRIGGER trg_audit_insert
AFTER INSERT ON Events
FOR EACH ROW
BEGIN
  INSERT INTO AuditLogs(action, table_name, record_id, new_data)
  VALUES('INSERT','Events',NEW.event_id,NEW.title);
END;
CREATE TRIGGER trg_audit_update
AFTER UPDATE ON Events
FOR EACH ROW
BEGIN
  INSERT INTO AuditLogs(action, table_name, record_id, old_data, new_data)
  VALUES('UPDATE','Events',NEW.event_id,OLD.title,NEW.title);
END;
CREATE TRIGGER trg_auto_complete_event
AFTER UPDATE ON Events
FOR EACH ROW
WHEN NEW.status = 'active' AND julianday('now') > julianday(NEW.end_time)
BEGIN
  UPDATE Events SET status='completed' WHERE event_id=NEW.event_id;
END;
CREATE TRIGGER trg_event_admin_college
BEFORE INSERT ON Events
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (SELECT college_id FROM Admins WHERE admin_id = NEW.created_by) <> NEW.college_id
    THEN RAISE(ABORT, 'Admin and Event college mismatch')
  END;
END;
CREATE TRIGGER trg_event_capacity_check
BEFORE INSERT ON Registrations
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (SELECT COUNT(*) FROM Registrations WHERE event_id = NEW.event_id AND status = 'registered')
      >= (SELECT capacity FROM Events WHERE event_id = NEW.event_id)
      THEN RAISE(ABORT, 'Event capacity reached')
  END;
END;
CREATE TRIGGER trg_event_capacity_update
BEFORE UPDATE OF status ON Registrations
FOR EACH ROW
WHEN NEW.status = 'registered'
BEGIN
  SELECT CASE
    WHEN (SELECT COUNT(*) FROM Registrations WHERE event_id = OLD.event_id AND status = 'registered')
      >= (SELECT capacity FROM Events WHERE event_id = OLD.event_id)
      THEN RAISE(ABORT, 'Event capacity reached')
  END;
END;
CREATE TRIGGER trg_feedback_requires_attendance
BEFORE INSERT ON Feedback
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN NOT EXISTS (SELECT 1 FROM Attendance a WHERE a.registration_id=NEW.registration_id AND a.attended=1)
      THEN RAISE(ABORT, 'Feedback allowed only for attendees')
  END;

  SELECT CASE
    WHEN (SELECT e.status
          FROM Events e
          JOIN Registrations r ON e.event_id=r.event_id
          WHERE r.registration_id=NEW.registration_id) <> 'completed'
      THEN RAISE(ABORT, 'Feedback only after event completion')
  END;
END;
CREATE TRIGGER trg_no_capacity_below_existing
BEFORE UPDATE OF capacity ON Events
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN NEW.capacity < (SELECT COUNT(*) FROM Registrations WHERE event_id = OLD.event_id AND status='registered')
      THEN RAISE(ABORT, 'New capacity below existing registrations')
  END;
END;
CREATE TRIGGER trg_registration_event_status
BEFORE INSERT ON Registrations
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (SELECT status FROM Events WHERE event_id = NEW.event_id) IN ('cancelled','completed')
      THEN RAISE(ABORT, 'Cannot register for closed event')
  END;
  SELECT CASE
    WHEN julianday(datetime('now')) > (SELECT julianday(end_time) FROM Events WHERE event_id = NEW.event_id)
      THEN RAISE(ABORT, 'Registration closed (event ended)')
  END;
END;
CREATE TRIGGER trg_registration_same_college
BEFORE INSERT ON Registrations
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (SELECT college_id FROM Students WHERE student_id = NEW.student_id)
      <> (SELECT college_id FROM Events WHERE event_id = NEW.event_id)
    THEN RAISE(ABORT, 'Student and Event belong to different colleges')
  END;
END;
COMMIT;
