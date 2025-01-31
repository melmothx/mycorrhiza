-- 1 up
CREATE TABLE amc_sessions (
   sid VARCHAR(64) PRIMARY  KEY,
   compiler_options JSONB NULL,
   job_id INTEGER NULL,
   compiled_file TEXT NULL,
   logs JSONB NULL,
   created TIMESTAMP WITH TIME ZONE NOT NULL,
   last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE amc_session_files (
   id SERIAL NOT NULL PRIMARY KEY,
   sid VARCHAR(64) NOT NULL REFERENCES amc_sessions(sid) ON DELETE CASCADE ON UPDATE CASCADE,
   basename VARCHAR(255) NULL,
   original_filename VARCHAR(255) NOT NULL,
   sorting_index INTEGER NOT NULL,
   attributes JSONB NULL,
   file_size INTEGER NOT NULL,
   created TIMESTAMP WITH TIME ZONE NOT NULL,
   last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 1 down
DROP TABLE amc_sessions;
DROP TABLE amc_session_files;

-- 2 up

ALTER TABLE amc_sessions ADD COLUMN session_type VARCHAR(32) DEFAULT 'bookbuilder';

-- 2 down

ALTER TABLE amc_sessions DROP COLUMN session_type;
