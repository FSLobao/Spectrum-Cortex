# CREATE DATABASE
CREATE SCHEMA cortex;
USE cortex;
CREATE TABLE Modules (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the modules that may be integrated into the measurement stations', 
  ID TEXT NULL COMMENT 'Unique identifier to a module, combination of manufacturer, model, serial number and version. Maintenance and updates should generate new registers on this table',
  Tag TEXT NULL COMMENT 'Multiple identifiers that may apply to  characterize the module, e.g. antenna, receiver, cable',
  PortID TEXT NULL COMMENT 'Multiple identifiers that may apply to identify how the module is referenced on the data, e.g. 1, 2, Port A',
  PRIMARY KEY (PK));
CREATE TABLE Stations (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to measurement stations at an specific configuration',
  ID TEXT NULL COMMENT 'Unique identifier to a station, combination of model and serial number at an specific version, considering modules installed',
  Tag TEXT NULL COMMENT 'Multiple identifiers that may apply to  characterize the station, e.g. fix monitoring, transportable, narrowband',
  PRIMARY KEY (PK));
CREATE TABLE RT_Station_Module (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to associations between modules and stations',
  FK_Station INT NOT NULL,
  FK_Module INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Station) REFERENCES Stations (PK),
  FOREIGN KEY (FK_Module) REFERENCES Modules (PK));
CREATE TABLE Sites (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to sites, places defined by latitude and longitude and where a measurement was performed or an emitter is located',
  Coordinates VARCHAR(255) NULL,
  ID TEXT NULL,
  Tag TEXT NULL,
  PRIMARY KEY (PK));
CREATE TABLE RawData_Files (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to raw data file.',
  FK_Station INT NULL,
  FK_Site INT NULL,
  Hz_Start INT(12) NULL COMMENT 'Initial frequency expressed in Hz',
  Hz_Stop INT(12) NULL COMMENT 'End frequency expressed in Hz',
  Time_Start DATETIME NULL COMMENT 'Initial time expressed in GMT',
  Time_Stop DATETIME NULL COMMENT 'End time expressed in GMT',
  Tag TEXT NULL COMMENT 'file format, such as e.g. BIN, HDF5, WAV, NCP',
  FileName TEXT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Station) REFERENCES Stations (PK),
  FOREIGN KEY (FK_Site) REFERENCES Sites (PK));
CREATE TABLE Emissions (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to emissions that may have been identified',
  Hz_Start INT(12) NULL COMMENT 'Initial frequency expressed in Hz',
  Hz_Stop INT(12) NULL COMMENT 'End frequency expressed in Hz',
  Time_Start DATETIME NULL COMMENT 'Initial time expressed in GMT',
  Time_Stop DATETIME NULL COMMENT 'End time expressed in GMT',
  Power_Map TEXT NULL,
  Max_Power DECIMAL(10,4) NULL COMMENT 'Maximum power expressed in dBmW/m² = dBµV/m – 115.8', 
  Min_Power DECIMAL(10,4) NULL COMMENT 'Minimum power expressed in dBmW/m² = dBµV/m – 115.8',
  On_Map TEXT NULL,
  Off_Map TEXT NULL,
  Tag TEXT NULL COMMENT 'e.g. Digital, Analog, Duplex, Broadcast, PAL, Radio, TV, Mobile',
  Emitter_ID_tag TEXT NULL COMMENT 'e.g. identified, probable, multiple, unknown',
  Channel_ID_tag TEXT NULL COMMENT 'e.g. unique, probable, multiple, unknown',
  PRIMARY KEY (PK));
CREATE TABLE RT_RawData_Emission (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the table that associates emissionns and files',
  FK_RawData_File INT NOT NULL,
  FK_Emission INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_RawData_File) REFERENCES RawData_Files (PK),
  FOREIGN KEY (FK_Emission) REFERENCES Emissions (PK));
CREATE TABLE Noise (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the noise table. ',
  Hz_Start INT(12) NULL COMMENT 'Initial frequency expressed in Hz',
  Hz_Stop INT(12) NULL COMMENT 'End frequency expressed in Hz',
  Time_Start DATETIME NULL COMMENT 'Initial time expressed in GMT',
  Time_Stop DATETIME NULL COMMENT 'End time expressed in GMT',
  Power_Map TEXT NULL,
  Max_Power DECIMAL(10,4) NULL COMMENT 'Maximum power expressed in dBmW/m² = dBµV/m – 115.8', 
  Min_Power DECIMAL(10,4) NULL COMMENT 'Minimum power expressed in dBmW/m² = dBµV/m – 115.8',
  Tag TEXT NULL COMMENT 'High, Medium, Low',
  PRIMARY KEY (PK));
CREATE TABLE RT_RawData_Noise (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the table that associates emissionns and files',
  FK_RawData_File INT NOT NULL,
  FK_Noise_Block INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_RawData_File) REFERENCES RawData_Files (PK),
  FOREIGN KEY (FK_Noise_Block) REFERENCES Noise (PK));
CREATE TABLE Services (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to table that list the telecomunications services',
  ID TEXT NULL COMMENT '',
  Designation TEXT NULL COMMENT '',
  Tag TEXT NULL COMMENT 'e.g. Colective, Private',
  Icon TEXT NULL COMMENT 'Image file representation for maps and graphs other raster presentation',
  Colour TEXT NULL COMMENT 'Colour representation for vectorial presentation',
  PRIMARY KEY (PK));
CREATE TABLE Emitters (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to table that list the licensed emitters',
  ID TEXT NULL COMMENT '',
  Designation TEXT NULL COMMENT '',
  Tag TEXT NULL COMMENT 'e.g. fixed, mobile',
  FK_Site INT NOT NULL,
  FK_Service INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Service) REFERENCES Services (PK),
  FOREIGN KEY (FK_Site) REFERENCES Sites (PK));
CREATE TABLE RT_Emitter_Emission (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the table that associates identified emitters and their emissionns',
  FK_Emitter INT NOT NULL,
  FK_Emission INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Emitter) REFERENCES Emitters (PK),
  FOREIGN KEY (FK_Emission) REFERENCES Emissions (PK));
CREATE TABLE Regulations (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the list of regulations.',
  FK_Service INT NOT NULL,
  Table_ID TEXT NULL,
  TableName TEXT NULL,
  Downlink BOOLEAN NULL,
  Channel_Spacing INT(10) NULL COMMENT 'Channel spacing expressed in Hz', 
  Flags TEXT NULL,
  Power_Limit DECIMAL(10,4) NULL COMMENT 'Power expressed in dBmW/m², converted from transmitter power as EIRP',
  Modulation_Type TEXT NULL,
  Required_Mod TEXT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Service) REFERENCES Services (PK));
CREATE TABLE Channels (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to table that channels defined by regulations',
  ID TEXT NULL COMMENT '',
  Hz_Center INT(12) NULL COMMENT 'Center frequency expressed in Hz',
  FK_Regulation INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Regulation) REFERENCES Regulations (PK));
CREATE TABLE RT_Channel_Emission (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to the table that associates existing channels and emissionns',
  FK_Channel INT NOT NULL,
  FK_Emission INT NOT NULL,
  PRIMARY KEY (PK),
  FOREIGN KEY (FK_Channel) REFERENCES Channels (PK),
  FOREIGN KEY (FK_Emission) REFERENCES Emissions (PK));
CREATE TABLE Asignations (
  PK INT NOT NULL AUTO_INCREMENT COMMENT 'Primary Key to table that list asignated ',
  Label TEXT NULL COMMENT '',
  Icon TEXT NULL COMMENT '',
  Hz_Start INT(12) NULL COMMENT 'Initial frequency expressed in Hz',
  Hz_Stop INT(12) NULL COMMENT 'End frequency expressed in Hz',
  PRIMARY KEY (PK));

# CREATE VIEWS TO BE USED BY JOOMLA
CREATE 
    ALGORITHM = MERGE 
    DEFINER = root@localhost 
    SQL SECURITY DEFINER
VIEW cortex.RawData_Files_View AS
    SELECT 
        cortex.RawData_Files.PK AS PK,
        cortex.RawData_Files.Hz_Start AS Hz_Start,
        cortex.RawData_Files.Hz_Stop AS Hz_Stop,
        cortex.RawData_Files.Time_Start AS Time_Start,
        cortex.RawData_Files.Time_Stop AS Time_Stop,
        cortex.RawData_Files.Tag AS File_Tag,
        cortex.RawData_Files.FileName AS FileName,
        cortex.RawData_Files.FK_Site AS FK_Site,
        cortex.Sites.Coordinates AS Coordinates,
        cortex.Sites.ID AS Site_ID,
        cortex.Sites.Tag AS Site_Tag,
        cortex.RawData_Files.FK_Station AS FK_Station,
        cortex.Stations.ID AS Station_ID,
        cortex.Stations.Tag AS Station_Tag
    FROM
        ((cortex.RawData_Files
        JOIN cortex.Sites ON ((cortex.RawData_Files.FK_Site = cortex.Sites.PK)))
        JOIN cortex.Stations ON ((cortex.RawData_Files.FK_Station = cortex.Stations.PK)));

CREATE 
    ALGORITHM = MERGE 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `cortex`.`Channel_Regulation_View` AS
    SELECT 
        `cortex`.`Channels`.`PK` AS `PK`,
        `cortex`.`Channels`.`ID` AS `Channel_ID`,
        `cortex`.`Channels`.`Hz_Center` AS `Hz_Center`,
        `cortex`.`Regulations`.`PK` AS `FK_Regulations`,
        `cortex`.`Regulations`.`Table_ID` AS `Table_ID`,
        `cortex`.`Regulations`.`TableName` AS `TableName`,
        `cortex`.`Regulations`.`Downlink` AS `Downlink`,
        `cortex`.`Regulations`.`Channel_Spacing` AS `Channel_Spacing`,
        `cortex`.`Regulations`.`Flags` AS `Flags`,
        `cortex`.`Regulations`.`Power_Limit` AS `Power_Limit`,
        `cortex`.`Regulations`.`Modulation_Type` AS `Modulation_Type`,
        `cortex`.`Regulations`.`Required_Mod` AS `Required_Mod`,
        `cortex`.`Regulations`.`FK_Service` AS `FK_Service`
    FROM
        (`cortex`.`Channels`
        JOIN `cortex`.`Regulations` ON ((`cortex`.`Channels`.`FK_Regulation` = `cortex`.`Regulations`.`PK`)));
        
CREATE 
    ALGORITHM = MERGE 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `cortex`.`Channel_Regulation_Service_View` AS
    SELECT 
        `JCR`.`PK` AS `PK`,
        `JCR`.`Channel_ID` AS `Channel_ID`,
        `JCR`.`Hz_Center` AS `Hz_Center`,
        `JCR`.`FK_Regulations` AS `FK_Regulations`,
        `JCR`.`Table_ID` AS `Table_ID`,
        `JCR`.`TableName` AS `TableName`,
        `JCR`.`Downlink` AS `Downlink`,
        `JCR`.`Channel_Spacing` AS `Channel_Spacing`,
        `JCR`.`Flags` AS `Flags`,
        `JCR`.`Power_Limit` AS `Power_Limit`,
        `JCR`.`Modulation_Type` AS `Modulation_Type`,
        `JCR`.`Required_Mod` AS `Required_Mod`,
        `cortex`.`Services`.`PK` AS `FK_Service`,
        `cortex`.`Services`.`ID` AS `Service_ID`,
        `cortex`.`Services`.`Designation` AS `Designation`,
        `cortex`.`Services`.`Tag` AS `Service_Tag`,
        `cortex`.`Services`.`Icon` AS `Icon`,
        `cortex`.`Services`.`Colour` AS `Colour`
    FROM
        (`cortex`.`Channel_Regulation_View` `JCR`
        JOIN `cortex`.`Services` ON ((`JCR`.`FK_Service` = `cortex`.`Services`.`PK`)));
        
CREATE 
    ALGORITHM = MERGE 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW cortex.Emitter_View AS
    SELECT 
        Emit.PK AS PK,
        Emit.ID AS Emitter_ID,
        Emit.Designation AS Emitter_Designation,
        Emit.Tag AS Emitter_Tag,
        JSiE.PK AS FK_Site,
        JSiE.Coordinates AS Coordinates,
        JSiE.ID AS Site_ID,
        JSiE.Tag AS Site_Tag,
        JSeE.PK AS Service_PK,
        JSeE.ID AS Service_ID,
        JSeE.Designation AS Service_Designation,
        JSeE.Tag AS Service_Tag,
        JSeE.Icon AS Icon,
        JSeE.Colour AS Colour
    FROM (cortex.Emitters AS Emit
	JOIN cortex.Sites AS JSiE 
		ON (JSiE.PK = Emit.FK_Site) 
	JOIN cortex.Services AS JSeE
		ON (JSeE.PK = Emit.FK_Service)  )
