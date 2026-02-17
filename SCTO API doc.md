Server API v2
Welcome to the SurveyCTO Server API v2 documentation. This API provides comprehensive access to managing datasets, records and more.

Base URL

https://your-server.surveycto.com/api/v2
Replace your-server with your actual SurveyCTO server name.

API Reference
Datasets
Operations
GET
/api/v2/datasets
POST
/api/v2/datasets
GET
/api/v2/datasets/data/csv/{datasetID:.+}
GET
/api/v2/datasets/{datasetId}
PUT
/api/v2/datasets/{datasetId}
DELETE
/api/v2/datasets/{datasetId}
POST
/api/v2/datasets/{datasetId}/purge
Hide operations
List all datasets
Retrieves a paginated list of datasets that the authenticated user has access to. Results can be filtered by team and ordered by specified fields. The endpoint uses cursor-based pagination for efficient data retrieval.

Parameters
Query Parameters
cursor
URL-encoded cursor for pagination. Use the 'nextCursor' value from the previous response to retrieve the next page of results. If not provided, returns the first page.

Type
string
Example
sample_cases
limit
Maximum number of datasets to return per page. Must be between 1 and 1000.

Type
integer
maximum
1000
default
20
orderBy
Field to sort the results by.

Type
string
Enum
id
title
createdOn
modifiedOn
status
version
discriminator
default
createdOn
orderByDirection
Sort direction for the orderBy field.

Type
string
Enum
ASC
DESC
default
ASC
teamId
Filter datasets by team ID. If provided, only datasets accessible to the specified team will be returned. The user must have appropriate permissions to access the team's datasets.

Type
string
Example
team-456
Responses

200
Successful operation - Returns paginated list of datasets
Content-Type
application/json
Schema
Success Response Example


object
Generic paginated response using cursor-based pagination for efficient data retrieval


nextCursor
string
Cursor for retrieving the next page. If null, there are no more pages available.


total
long
Total number of items available across all pages


data
array
Array of data items for the current page


limit
integer
Page size limit for pagination. Maximum allowed is 1000 items per request.


GET
/api/v2/datasets
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets?cursor=sample_cases&teamId=team-456'
Create dataset
Creates a new dataset with the specified configuration.

Request Body
application/json
Schema
Cases Dataset Example
Enum Dataset Example


object

Input model for creating and updating datasets with all required configuration options


idFormatOptions

object
Configuration options for ID format used in auto-generation of enumerator IDs


allowOfflineUpdates
boolean
Whether the dataset allows offline updates.


id
string
Unique identifier for the dataset. Must be unique across the system.


title
string
Display title for the dataset.


casesManagementOptions

object
Configuration options for cases management.


locationContext

object

Context for positioning the dataset within the group hierarchy and relative to other items


discriminator
string
Valid values
CASES
ENUMERATORS
DATA

uniqueRecordField
string
Field name to use for unique record identification.

Responses

200
OK - Dataset created successfully
Content-Type
application/json
Schema
Enum Dataset Response
Cases Dataset Response


object


idFormatOptions

object
Configuration options for ID format used in auto-generation of enumerator IDs


totalRecords
integer
Number of rows/records in the dataset


groupId
integer
ID of the group that owns this dataset. Groups are used to organize and control access to datasets.


fieldNames
string
Comma-separated list of field names


title
string
Dataset title


createdOn
string
Dataset creation date


version
integer
Dataset version number


discriminator
string
Valid values
CASES
ENUMERATORS
DATA

uniqueRecordField
string
Field name used for unique record identification


modifiedOn
string
Dataset last modification date


allowOfflineUpdates
boolean
Whether offline updates are allowed


id
string
Dataset identifier


casesManagementOptions

object
Configuration options for cases management.


lastIncomingDataDate
string
Timestamp of the last incoming data


status
string
Possible values:

• READY: Dataset is ready for use, all data is synchronized and up-to-date
• DIRTY: Dataset is currently being synchronized, data may be incomplete or in transition

Valid values
READY
DIRTY

POST
/api/v2/datasets
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets \
  --request POST \
  --header 'Content-Type: application/json'
Download dataset data in CSV format
Downloads data from a dataset in CSV format. The CSV includes all rows and columns from the dataset with proper UTF-8 encoding. You can optionally download the file as an attachment with a specific filename.

Parameters
Path Parameters
datasetId
*
The unique identifier of the server dataset for which to download CSV data.

Type
string
Required
Query Parameters
asAttachment
Optional flag to specify whether the file should be downloaded as an attachment.

Type
boolean
default
false
Responses

200
Successfully downloaded dataset CSV data
Content-Type
text/csv
Schema
CSV file example


object

GET
/api/v2/datasets/data/csv/{datasetID:.+}
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/data/csv/{datasetID:.+}'
Get single dataset
Retrieves detailed information about a specific dataset by its ID. Returns comprehensive dataset metadata including configuration options, status, and statistics.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to retrieve. This is the dataset's ID as it appears in the system.

Type
string
Required
Example
cases
Responses
200
401
403
404
500
OK - Dataset found and returned successfully
Content-Type
application/json
Schema
Success Response Example


object


idFormatOptions

object
Configuration options for ID format used in auto-generation of enumerator IDs


totalRecords
integer
Number of rows/records in the dataset


groupId
integer
ID of the group that owns this dataset. Groups are used to organize and control access to datasets.


fieldNames
string
Comma-separated list of field names


title
string
Dataset title


createdOn
string
Dataset creation date


version
integer
Dataset version number


discriminator
string
Valid values
CASES
ENUMERATORS
DATA

uniqueRecordField
string
Field name used for unique record identification


modifiedOn
string
Dataset last modification date


allowOfflineUpdates
boolean
Whether offline updates are allowed


id
string
Dataset identifier


casesManagementOptions

object
Configuration options for cases management.


lastIncomingDataDate
string
Timestamp of the last incoming data


status
string
Possible values:

• READY: Dataset is ready for use, all data is synchronized and up-to-date
• DIRTY: Dataset is currently being synchronized, data may be incomplete or in transition

Valid values
READY
DIRTY

GET
/api/v2/datasets/{datasetId}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases
Update dataset
Updates an existing dataset with the specified configuration. Only provided fields will be updated. The discriminator cannot be changed after creation and the uniqueRecordField cannot be updated if already set.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to update. This must match an existing dataset in the system.

Type
string
Required
Example
cases
Request Body
application/json
Schema
Update Dataset Example


object

Input model for creating and updating datasets with all required configuration options


idFormatOptions

object
Configuration options for ID format used in auto-generation of enumerator IDs


allowOfflineUpdates
boolean
Whether the dataset allows offline updates.


id
string
Unique identifier for the dataset. Must be unique across the system.


title
string
Display title for the dataset.


casesManagementOptions

object
Configuration options for cases management.


locationContext

object

Context for positioning the dataset within the group hierarchy and relative to other items


discriminator
string
Valid values
CASES
ENUMERATORS
DATA

uniqueRecordField
string
Field name to use for unique record identification.

Responses

200
OK - Dataset updated successfully
Content-Type
application/json
Schema
Updated Dataset Response


object


idFormatOptions

object
Configuration options for ID format used in auto-generation of enumerator IDs


totalRecords
integer
Number of rows/records in the dataset


groupId
integer
ID of the group that owns this dataset. Groups are used to organize and control access to datasets.


fieldNames
string
Comma-separated list of field names


title
string
Dataset title


createdOn
string
Dataset creation date


version
integer
Dataset version number


discriminator
string
Valid values
CASES
ENUMERATORS
DATA

uniqueRecordField
string
Field name used for unique record identification


modifiedOn
string
Dataset last modification date


allowOfflineUpdates
boolean
Whether offline updates are allowed


id
string
Dataset identifier


casesManagementOptions

object
Configuration options for cases management.


lastIncomingDataDate
string
Timestamp of the last incoming data


status
string
Possible values:

• READY: Dataset is ready for use, all data is synchronized and up-to-date
• DIRTY: Dataset is currently being synchronized, data may be incomplete or in transition

Valid values
READY
DIRTY

PUT
/api/v2/datasets/{datasetId}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases \
  --request PUT \
  --header 'Content-Type: application/json'
Delete dataset
Permanently deletes a dataset and all its associated data. This operation cannot be undone. Returns a success message indicating whether the deletion was successful.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to delete. This must match an existing dataset in the system.

Type
string
Required
Example
cases
Responses
200
401
403
404
500
OK - Dataset deletion completed (check success field for actual result)
Content-Type
application/json
Schema
Failed Deletion
Successful Deletion


object
Generic response indicating the result of an operation with success status and descriptive message


success
boolean
Whether the operation was successful


message
string
Descriptive message about the operation result


DELETE
/api/v2/datasets/{datasetId}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases \
  --request DELETE
Purge dataset
Removes all data from the dataset while keeping the dataset structure intact. This operation clears all records but preserves the dataset configuration and metadata. Returns a success message indicating whether the purge was successful.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to purge. This must match an existing dataset in the system.

Type
string
Required
Example
cases
Responses
200
401
403
404
500
OK - Dataset purge completed (check success field for actual result)
Content-Type
application/json
Schema
Failed Purge
Successful Purge


object
Generic response indicating the result of an operation with success status and descriptive message


success
boolean
Whether the operation was successful


message
string
Descriptive message about the operation result


POST
/api/v2/datasets/{datasetId}/purge
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases/purge \
  --request POST
Dataset Records
Operations
GET
/api/v2/datasets/{datasetId}/record
PUT
/api/v2/datasets/{datasetId}/record
DELETE
/api/v2/datasets/{datasetId}/record
PATCH
/api/v2/datasets/{datasetId}/record
GET
/api/v2/datasets/{datasetId}/records
POST
/api/v2/datasets/{datasetId}/records
POST
/api/v2/datasets/{datasetId}/records/upload
Hide operations
Get single record from dataset
Retrieves a specific record from a dataset using its unique record ID. The dataset must have a uniqueRecordField configured to use this endpoint. Returns the record data along with modification timestamp.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset containing the record

Type
string
Required
Example
cases
Query Parameters
recordId
*
The unique identifier of the record to retrieve. Uses query parameter to handle special characters safely.

Type
string
Required
Example
1
Responses

200
OK - Record found and returned successfully
Content-Type
application/json
Schema
Success Response Example


object

Response containing a dataset record with its data and metadata


recordId
string
The unique identifier of the record


modifiedAt
string
Timestamp when the record was last modified (UTC)


values

object
The record data as key-value pairs. Fields depend on the dataset structure.


GET
/api/v2/datasets/{datasetId}/record
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/cases/record?recordId=1'
Update record in dataset
Updates an existing record in the specified dataset. The record must already exist. Only provided fields will be updated, missing fields remain unchanged. New fields in the request body will be added as new columns to the dataset. Returns the updated record data with metadata.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset containing the record to update

Type
string
Required
Example
cases
Query Parameters
recordId
*
The unique identifier of the record to update. The record must already exist in the dataset.

Type
string
Required
Example
1
Request Body
application/json
Schema
Update Record Example


object
Record data as key-value pairs where all keys are field names and all values are strings

Responses

200
OK - Record updated successfully
Content-Type
application/json
Schema
Updated Record Response


object

Response containing a dataset record with its data and metadata


recordId
string
The unique identifier of the record


modifiedAt
string
Timestamp when the record was last modified (UTC)


values

object
The record data as key-value pairs. Fields depend on the dataset structure.


PUT
/api/v2/datasets/{datasetId}/record
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/cases/record?recordId=1' \
  --request PUT \
  --header 'Content-Type: application/json'
Delete record from dataset
Permanently deletes a specific record from the dataset using its unique record ID. The dataset must have a uniqueRecordField configured and the record must exist. This operation cannot be undone. Returns a success message indicating whether the deletion was successful.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset containing the record to delete

Type
string
Required
Example
cases
Query Parameters
recordId
*
The unique identifier of the record to delete. The record must exist in the dataset.

Type
string
Required
Example
1
Responses

200
OK - Record deletion completed (check success field for actual result)
Content-Type
application/json
Schema
Failed Deletion
Successful Deletion


object
Generic response indicating the result of an operation with success status and descriptive message


success
boolean
Whether the operation was successful


message
string
Descriptive message about the operation result


DELETE
/api/v2/datasets/{datasetId}/record
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/cases/record?recordId=1' \
  --request DELETE
Upsert record in dataset
Updates an existing record or creates a new one if it doesn't exist. Only provided fields will be updated/set, missing fields remain unchanged. New fields in the request body will be added as new columns to the dataset. Returns the upserted record data with metadata.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to upsert the record in

Type
string
Required
Example
cases
Query Parameters
recordId
*
The unique identifier of the record to upsert. If the record doesn't exist, it will be created.

Type
string
Required
Example
1
Request Body
application/json
Schema
Upsert Record Example


object
Record data as key-value pairs where all keys are field names and all values are strings

Responses

200
OK - Record upserted successfully (created or updated)
Content-Type
application/json
Schema
Upserted Record Response


object

Response containing a dataset record with its data and metadata


recordId
string
The unique identifier of the record


modifiedAt
string
Timestamp when the record was last modified (UTC)


values

object
The record data as key-value pairs. Fields depend on the dataset structure.


PATCH
/api/v2/datasets/{datasetId}/record
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/cases/record?recordId=1' \
  --request PATCH \
  --header 'Content-Type: application/json'
Get all records from dataset
Retrieves a paginated list of all records from the specified dataset with optional filtering and sorting. Supports cursor-based pagination for efficient data retrieval. Records can be filtered by modification time and sorted by any field. The dataset must have a uniqueRecordField configured.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to retrieve records from

Type
string
Required
Example
cases
Query Parameters
cursor
ID of the record to serve as the pagination cursor. Records after this cursor will be returned based on the sort order. For the first page, omit this parameter. Special characters in the ID must be URL-encoded.

Type
string
Example
ENUM_00174
limit
Number of records to fetch per page. Must be between 1 and 1000.

Type
integer
maximum
1000
default
20
orderBy
Field to sort the records by. Must be a valid field in the dataset or 'modifiedAt'.

Type
string
Example
name
default
modifiedAt
orderByDirection
Sort direction for the orderBy field.

Type
string
Enum
ASC
DESC
Example
ASC
default
ASC
modifiedAt.gt
Return records where modifiedAt is greater than the given ISO 8601 timestamp. Cannot be used together with modifiedAt.gte.

Type
string
Example
2025-06-01T00:00:00Z
modifiedAt.gte
Return records where modifiedAt is greater than or equal to the given ISO 8601 timestamp. Cannot be used together with modifiedAt.gt.

Type
string
Example
2025-06-01T00:00:00Z
modifiedAt.lt
Return records where modifiedAt is less than the given ISO 8601 timestamp. Cannot be used together with modifiedAt.lte.

Type
string
Example
2025-06-01T23:59:59Z
modifiedAt.lte
Return records where modifiedAt is less than or equal to the given ISO 8601 timestamp. Cannot be used together with modifiedAt.lt.

Type
string
Example
2025-06-01T23:59:59Z
Responses

200
OK - Records retrieved successfully
Content-Type
application/json
Schema
Records List Response


object
Generic paginated response using cursor-based pagination for efficient data retrieval


nextCursor
string
Cursor for retrieving the next page. If null, there are no more pages available.


total
long
Total number of items available across all pages


data
array
Array of data items for the current page


limit
integer
Page size limit for pagination. Maximum allowed is 1000 items per request.


GET
/api/v2/datasets/{datasetId}/records
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/datasets/cases/records?cursor=ENUM_00174&orderBy=name&orderByDirection=ASC&modifiedAt.gt=2025-06-01T00%3A00%3A00Z&modifiedAt.gte=2025-06-01T00%3A00%3A00Z&modifiedAt.lt=2025-06-01T23%3A59%3A59Z&modifiedAt.lte=2025-06-01T23%3A59%3A59Z'
Add record to dataset
Creates a new record in the specified dataset. For datasets with a unique record field configured, the unique field value must be provided and must not already exist. The system will automatically add any missing columns to accommodate new fields. Returns the created record data.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to add the record to

Type
string
Required
Example
cases
Request Body
application/json
Schema
Add Record Example


object
Record data as key-value pairs where all keys are field names and all values are strings

Responses

200
OK - Record created successfully
Content-Type
application/json
Schema
Success Response Example


object

Response containing a dataset record with its data and metadata


recordId
string
The unique identifier of the record


modifiedAt
string
Timestamp when the record was last modified (UTC)


values

object
The record data as key-value pairs. Fields depend on the dataset structure.


POST
/api/v2/datasets/{datasetId}/records
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases/records \
  --request POST \
  --header 'Content-Type: application/json'
Upload records to dataset
Uploads records from a CSV file to the specified dataset. Supports different upload modes: APPEND (add new records), MERGE (update existing records based on unique field), or CLEAR (replace all data). The system will automatically add missing columns and return detailed statistics about the upload operation.

Parameters
Path Parameters
datasetId
*
The unique identifier of the dataset to upload records to

Type
string
Required
Example
cases
Request Body
multipart/form-data
Schema
Upload with Metadata Example


object

Multipart form data for uploading records to a dataset


metadata

object
Metadata for configuring how the uploaded data should be processed


file
string
CSV file containing the records to upload (must be smaller than 100MB)

Responses

200
OK - Records uploaded successfully
Content-Type
application/json
Schema
Upload Response Example


object
Summary of changes made to the dataset during the upload operation


errorMessages
string[]
List of error messages encountered during the upload


rowsAdded
integer
Number of new records added to the dataset


rowsUpdated
integer
Number of existing records updated in the dataset


valuesTruncated
integer
Number of values that were truncated due to length constraints (maximum length is 255 characters)


enumeratorDatasetLinkedMessage
string
Message about enumerator dataset linking, if applicable


columnsAdded
integer
Number of new columns added to the dataset


POST
/api/v2/datasets/{datasetId}/records/upload
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/datasets/cases/records/upload \
  --request POST \
  --header 'Content-Type: multipart/form-data'
Forms
Operations
GET
/api/v2/forms/data/wide/json/{formID:.+}
GET
/api/v2/forms/ids
Hide operations
Download form data as JSON in wide format
Downloads form data as JSON in wide format using the v2 REST API. This is the recommended endpoint for JSON data downloads. Wide format consolidates all data into a single JSON array with repeat groups represented as nested structures. Key features: supports encrypted form data with private key upload, includes all field data (even fields not in current form definition), no data truncation, and requires a date parameter for incremental downloads. Rate limiting: For date=0 requests (all data), there is a 5-minute enforced quiet period between requests to prevent server overload.

Parameters
Path Parameters
formId
*
The unique identifier of the form for which to download JSON data in wide format. Wide format consolidates all data into a single JSON array with repeat groups as nested structures.

Type
string
Required
Query Parameters
date
*
Required. Date filter for incremental data downloads. Only submissions with CompletionDate on-and-after this date will be included. Use UTC time. Supports multiple formats: Unix time in seconds (≤12 digits), Unix time in milliseconds (≥13 digits), or URL-encoded string format. Special case: Use 0 or Jan%201%2C%201970%2000%3A00%3A00%20AM to get all data (subject to 5-minute rate limiting).

Type
string
Required
reviewStatuses
Optional comma-separated list of review statuses to filter the data. Valid values include: 'approved', 'rejected'.

Type
string
Responses

200
Successfully downloaded JSON data in wide format
Content-Type
application/json

GET
/api/v2/forms/data/wide/json/{formID:.+}
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/forms/data/wide/json/{formID:.+}'
List form IDs
Lists live form IDs (excluding drafts) and allows filtering by team. Returns all forms the user has access to, or forms specific to a team if teamId is provided.

Parameters
Query Parameters
teamId
Filter forms by team ID. If provided, only forms accessible to the specified team will be returned. The team must exist, not be paused, and the user must have the adequate permission.

Type
string
Example
team123
Responses

200
Successful operation - Returns list of form IDs
Content-Type
application/json
Schema
Success Response Example


object
Response containing list of form IDs


formIds
string[]
List of form IDs that the user has access to


GET
/api/v2/forms/ids
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/forms/ids?teamId=team123'
Submissions
Operations
GET
/api/v2/forms/{formID:.+}/submissions/{instanceID:.+}/attachments/{filename:.+}
Hide operations
Download submission attachment file
Downloads a specific attachment file from a form submission. For fields that have submission attachments, their field values in the JSON/CSV data will be URLs pointing to this endpoint. You can use those URLs or construct the URL manually using the template: /api/v2/forms/{formId}/submissions/{instanceId}/attachments/{filename}. Encrypted forms: For encrypted form attachments, the file will be served encrypted unless a private key is provided via POST request with multipart form data. The private key is used for decryption and is not stored on the server. Note: For encrypted forms, the server automatically appends '.enc' to filenames when retrieving encrypted attachments.

Parameters
Path Parameters
formId
*
The unique identifier of the form containing the submission with the attachment.

Type
string
Required
instanceId
*
The instance ID (KEY) of the specific submission containing the attachment. This is typically a UUID in the format 'uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'. Use the exact value from the KEY field in the submission data, including the 'uuid:' prefix.

Type
string
Required
filename
*
The filename of the attachment to download. This should be the exact filename as it appears in the submission data or attachment field value. For encrypted forms, do not include the '.enc' extension as the server will automatically append it when retrieving encrypted files.

Type
string
Required
Responses

200
Successfully downloaded the attachment file
Content-Type
*/*

GET
/api/v2/forms/{formID:.+}/submissions/{instanceID:.+}/attachments/{filename:.+}
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/forms/{formID:.+}/submissions/{instanceID:.+}/attachments/{filename:.+}'
Groups
Operations
GET
/api/v2/groups
Hide operations
List groups
Retrieves a paginated list of groups that the authenticated user has access to. Results can be filtered by parent group and ordered by specified fields. The endpoint uses cursor-based pagination for efficient data retrieval.

Parameters
Query Parameters
cursor
ID of the group to use as the pagination cursor. Returns groups that come after this cursor. Records are ordered by the orderBy field and direction. If not provided, return the first page.

Type
integer
Example
10
limit
Number of items to fetch. Must be between 1 and 1000.

Type
integer
maximum
1000
default
20
orderBy
Field to sort the results by.

Type
string
Enum
id
title
createdOn
default
createdOn
orderByDirection
Sort direction for the orderBy field.

Type
string
Enum
ASC
DESC
default
ASC
parentGroupId
Filter groups by parent group ID. If provided, only groups that are children of the specified parent group will be returned.

Type
integer
Example
5
Responses
200
400
401
403
500
Successful operation - Returns paginated list of groups
Content-Type
application/json
Schema
Success Response Example


object
Generic paginated response using cursor-based pagination for efficient data retrieval


nextCursor
string
Cursor for retrieving the next page. If null, there are no more pages available.


total
long
Total number of items available across all pages


data
array
Array of data items for the current page


limit
integer
Page size limit for pagination. Maximum allowed is 1000 items per request.


GET
/api/v2/groups
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/groups?cursor=10&parentGroupId=5'
Teams
Operations
GET
/api/v2/teams/ids
Hide operations
List team IDs
This admin-only endpoint returns a list of all team IDs. By default, it includes both active and paused teams. You can use the paused query parameter to filter the results and retrieve only active or only paused teams.

Parameters
Query Parameters
paused
Filter teams by their paused status. If true, returns only paused teams. If false, returns only active teams. If not provided, returns all teams (both active and paused).

Type
boolean
Responses
200
401
403
500
Successful operation - Returns list of team IDs
Content-Type
application/json
Schema
Success Response Example


object
Response containing list of team IDs


teamIds
string[]
List of team IDs


GET
/api/v2/teams/ids
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/teams/ids
Roles
Operations
GET
/api/v2/roles
GET
/api/v2/roles/{roleId}
Hide operations
Get all roles
Retrieves a paginated list of roles with customizable sorting options.

Parameters
Query Parameters
cursor
Role ID to serve as the cursor (case-sensitive). Roles after this one will be returned based on sort order. For the first page, omit this parameter.

Type
string
Example
admin
limit
Number of items to fetch. Must be between 1 and 1000.

Type
integer
maximum
1000
default
20
orderBy
Field to sort the results by. Must be one of: id, title, createdOn, createdBy.

Type
string
Enum
id
title
createdOn
createdBy
default
createdOn
orderByDirection
Sort direction for the orderBy field.

Type
string
Enum
ASC
DESC
default
ASC
Responses
200
400
401
403
500
OK - Roles retrieved successfully
Content-Type
application/json
Schema
Roles List Response


object
Generic paginated response using cursor-based pagination for efficient data retrieval


nextCursor
string
Cursor for retrieving the next page. If null, there are no more pages available.


total
long
Total number of items available across all pages


data
array
Array of data items for the current page


limit
integer
Page size limit for pagination. Maximum allowed is 1000 items per request.


GET
/api/v2/roles
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/roles?cursor=admin'
Get role permissions
Retrieves detailed permissions for a specific role, including system-level permissions and group-specific permissions. Group permissions can be filtered by providing a specific group ID.

Parameters
Path Parameters
roleId
*
The unique identifier of the role. Must match exact case (e.g., GLOBAL_ADMIN is valid, but global_admin is not).

Type
string
Required
Example
GLOBAL_ADMIN
Query Parameters
groupId
Filter group permissions by specific group ID. The group must exist and be accessible.

Type
integer
Example
25
Responses

200
OK - Role permissions retrieved successfully
Content-Type
application/json
Schema
Role Permissions Response


object

GET
/api/v2/roles/{roleId}
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/roles/GLOBAL_ADMIN?groupId=25'
Users
Operations
GET
/api/v2/users
POST
/api/v2/users
GET
/api/v2/users/{username}
PUT
/api/v2/users/{username}
DELETE
/api/v2/users/{username}
DELETE
/api/v2/users/bulk
POST
/api/v2/users/bulk/json
PUT
/api/v2/users/bulk/json
POST
/api/v2/users/bulk/file
PUT
/api/v2/users/bulk/file
Hide operations
List all users
Retrieves a paginated list of users with optional filtering by role and customizable sorting options.

Parameters
Query Parameters
cursor
URL-encoded username to serve as the cursor. Users after this one will be returned based on sort order. For the first page, omit this parameter.

Type
string
Example
john_doe@example.com
limit
Number of items to fetch. Must be between 1 and 1000.

Type
integer
maximum
1000
default
20
orderBy
Field to sort the results by. Must be one of: username, roleId, createdOn, modifiedOn.

Type
string
Enum
username
roleId
createdOn
modifiedOn
default
createdOn
orderByDirection
Sort direction for the orderBy field.

Type
string
Enum
ASC
DESC
default
ASC
roleId
Filter users by specific role ID (case-sensitive). The role must exist in the system.

Type
string
Example
GLOBAL_COLLECTOR
Responses
200
400
401
403
500
OK - Users retrieved successfully
Content-Type
application/json
Schema
Users List Response


object
Generic paginated response using cursor-based pagination for efficient data retrieval


nextCursor
string
Cursor for retrieving the next page. If null, there are no more pages available.


total
long
Total number of items available across all pages


data
array
Array of data items for the current page


limit
integer
Page size limit for pagination. Maximum allowed is 1000 items per request.


GET
/api/v2/users
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/users?cursor=john_doe%40example.com&roleId=GLOBAL_COLLECTOR'
Create user
Creates a new user with the specified configuration. Password requirements and validation rules depend on the role type and server configuration.

Request Body
application/json
Schema
Create User with Password
Let User Set Password


object
Input model for creating users with password and role configuration options


username
string
Unique username identifier for the user


passwordOption
string
Password setting option for the user account

Valid values
USER_SET_OWN
SET_NOW

password
string
Password for the user account. Required if passwordOption is SET_NOW.


confirmPassword
string
Password confirmation. Must match password field. Required if passwordOption is SET_NOW.


includePasswordInEmail
boolean
Whether to include the password in the email notification sent to the user. Only valid if passwordOption is SET_NOW.


roleId
string
Role identifier to assign to the user. The role must exist in the system.

Responses

200
OK - User created successfully
Content-Type
application/json
Schema
User Created Response


object
User information with basic details and metadata


username
string
Unique username identifier for the user


roleId
string
Role identifier assigned to the user


createdOn
string
Timestamp when the user was created

Format
date-time

modifiedOn
string
Timestamp when the user was last modified

Format
date-time

POST
/api/v2/users
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users \
  --request POST \
  --header 'Content-Type: application/json'
Get user by username
Retrieves a specific user by their username identifier.

Parameters
Path Parameters
username
*
The username of the user to retrieve

Type
string
Required
Example
john_doe
Responses
200
401
403
404
500
OK - User retrieved successfully
Content-Type
application/json
Schema
User Response


object
User information with basic details and metadata


username
string
Unique username identifier for the user


roleId
string
Role identifier assigned to the user


createdOn
string
Timestamp when the user was created

Format
date-time

modifiedOn
string
Timestamp when the user was last modified

Format
date-time

GET
/api/v2/users/{username}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/john_doe
Update user
Updates an existing user's role and/or password. At least one field (password or roleId) must be provided for update.

Parameters
Path Parameters
username
*
The username of the user to update

Type
string
Required
Example
john_doe
Request Body
application/json
Schema
Update Role Only
Update Password Only
Update Password and Role


object
Input model for updating user password and/or role


password
string
New password for the user account. If provided, confirmPassword is required.


confirmPassword
string
Password confirmation. Must match password field. Required if password is provided.


roleId
string
New role identifier to assign to the user. The role must exist in the system.

Responses

200
OK - User updated successfully
Content-Type
application/json
Schema
User Updated Response


object
User information with basic details and metadata


username
string
Unique username identifier for the user


roleId
string
Role identifier assigned to the user


createdOn
string
Timestamp when the user was created

Format
date-time

modifiedOn
string
Timestamp when the user was last modified

Format
date-time

PUT
/api/v2/users/{username}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/john_doe \
  --request PUT \
  --header 'Content-Type: application/json'
Delete user
Deletes an existing user by username. This operation is irreversible.

Parameters
Path Parameters
username
*
The username of the user to delete

Type
string
Required
Example
john_doe
Responses
200
401
403
404
500
OK - User deletion completed (check success field for actual result)
Content-Type
application/json
Schema
Failed Deletion
Successful Deletion


object
Generic API response wrapper


responseObject
string
Response data object


code
integer
Response status code


message
string
Response message or error description


DELETE
/api/v2/users/{username}
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/john_doe \
  --request DELETE
Bulk delete users
Deletes multiple users by providing an array of usernames. This operation is irreversible. Duplicate usernames are automatically removed.

Request Body
application/json
Schema
Simple Username List
Mixed Valid/Invalid Usernames

string[]
Responses
200
400
401
403
500
OK - Bulk user deletion completed (check individual results for success/failure details)
Content-Type
application/json
Schema
Bulk Delete Users Response


object

Response for bulk user deletion operation with detailed results


successful
string[]
List of usernames that were successfully deleted


failed

object[]
List of users that failed to be deleted with error details


summary

object
Summary statistics for bulk user operation


DELETE
/api/v2/users/bulk
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/bulk \
  --request DELETE \
  --header 'Content-Type: application/json'
Bulk create users from JSON
Creates multiple users by providing a JSON array of user data. Maximum 1000 users per request. The same validation rules from single user creation apply to each user.

Request Body
application/json
Schema
Mixed User Creation Example
User Set Own Password Example


object[]

username
string
Unique username identifier for the user


passwordOption
string
Password setting option for the user account

Valid values
USER_SET_OWN
SET_NOW

password
string
Password for the user account. Required if passwordOption is SET_NOW.


confirmPassword
string
Password confirmation. Must match password field. Required if passwordOption is SET_NOW.


includePasswordInEmail
boolean
Whether to include the password in the email notification sent to the user. Only valid if passwordOption is SET_NOW.


roleId
string
Role identifier to assign to the user. The role must exist in the system.

Responses

200
OK - Bulk user creation completed (check individual results for success/failure details)
Content-Type
application/json
Schema
Bulk Create Users JSON Response


object

Response for bulk user creation operation with detailed results


successful

object[]
List of successfully created users


failed

object[]
List of users that failed to be created with error details


summary

object
Summary statistics for bulk user operation


POST
/api/v2/users/bulk/json
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/bulk/json \
  --request POST \
  --header 'Content-Type: application/json'
Bulk update users from JSON
Updates multiple users by providing a JSON array of user data. The same validation rules from single user update apply to each user. Optionally supports upsert mode to create users if they don't exist.

Parameters
Query Parameters
upsert
Create users if they don't exist during update operation.

Type
boolean
Example
false
default
false
Request Body
application/json
Schema
Update Users Example
Upsert Mode Example


object[]

username
string
Unique username identifier for the user


passwordOption
string
Password setting option for the user account

Valid values
USER_SET_OWN
SET_NOW

password
string
Password for the user account. Required if passwordOption is SET_NOW.


confirmPassword
string
Password confirmation. Must match password field. Required if passwordOption is SET_NOW.


includePasswordInEmail
boolean
Whether to include the password in the email notification sent to the user. Only valid if passwordOption is SET_NOW.


roleId
string
Role identifier to assign to the user. The role must exist in the system.

Responses
200
400
401
403
500
OK - Bulk user update completed (check individual results for success/failure details)
Content-Type
application/json
Schema
Bulk Update Users JSON Response


object

Response for bulk user creation operation with detailed results


successful

object[]
List of successfully created users


failed

object[]
List of users that failed to be created with error details


summary

object
Summary statistics for bulk user operation


PUT
/api/v2/users/bulk/json
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/users/bulk/json?upsert=false' \
  --request PUT \
  --header 'Content-Type: application/json'
Bulk create users from file
Creates multiple users by uploading a CSV file. The CSV file must contain user data with proper headers. Maximum file size is 1MB and maximum 1000 users per request. The same validation rules from single user creation apply.

Parameters
Query Parameters
file
*
CSV file containing user data. Must include required headers: username, roleId. Optional headers: passwordOption, password, confirmPassword, includePasswordInEmail. Maximum file size: 1MB. Maximum users per file: 1000.

Type
string
Required
Request Body
multipart/form-data
Schema
CSV File Content Example


object

file
string
Format
binary
Responses

200
OK - Bulk user creation completed (check individual results for success/failure details)
Content-Type
application/json
Schema
Bulk Create Users Response


object

Response for bulk user creation operation with detailed results


successful

object[]
List of successfully created users


failed

object[]
List of users that failed to be created with error details


summary

object
Summary statistics for bulk user operation


POST
/api/v2/users/bulk/file
Samples

cURL

JavaScript

PHP

Python

curl https://your-server.surveycto.com/api/v2/users/bulk/file \
  --request POST \
  --header 'Content-Type: multipart/form-data'
Bulk update users from file
Updates multiple users by uploading a CSV file. The CSV file must contain user data with proper headers. Maximum 1000 users per request. The same validation rules from single user update apply. Optionally supports upsert mode to create users if they don't exist.

Parameters
Query Parameters
upsert
Create users if they don't exist during update operation.

Type
boolean
Example
false
default
false
file
*
CSV file containing user data. Must include required header: username. Optional headers: roleId, passwordOption, password, confirmPassword, includePasswordInEmail. Maximum users per file: 1000.

Type
string
Required
Request Body
multipart/form-data
Schema
CSV File Content Example


object

file
string
Format
binary
Responses
200
400
401
403
500
OK - Bulk user update completed (check individual results for success/failure details)
Content-Type
application/json
Schema
Bulk Update Users Response


object

Response for bulk user creation operation with detailed results


successful

object[]
List of successfully created users


failed

object[]
List of users that failed to be created with error details


summary

object
Summary statistics for bulk user operation


PUT
/api/v2/users/bulk/file
Samples

cURL

JavaScript

PHP

Python

curl 'https://your-server.surveycto.com/api/v2/users/bulk/file?upsert=false' \
  --request PUT \
  --header 'Content-Type: multipart/form-data'
Powered by VitePress OpenAPI
Pager
Previous page
Server API v1