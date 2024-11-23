-- 1 up
CREATE TABLE amc_sessions (
   sid VARCHAR(64) PRIMARY  KEY,
   created TIMESTAMP WITH TIME ZONE NOT NULL,
   last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE amc_session_files (
   id SERIAL NOT NULL PRIMARY KEY,
   sid VARCHAR(64) NOT NULL REFERENCES amc_sessions(sid) ON DELETE CASCADE ON UPDATE CASCADE,
   basename VARCHAR(255) NOT NULL,
   original_filename VARCHAR(255) NOT NULL,
   sorting_index INTEGER NOT NULL,
   file_size INTEGER NOT NULL,
   created TIMESTAMP WITH TIME ZONE NOT NULL,
   last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 1 down
DROP TABLE amc_sessions;
DROP TABLE amc_session_files;
