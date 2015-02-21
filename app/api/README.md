# Locations

## Get location info

API call:

    api/location/<location id>

  `location id` - The id of the location

Example return:

    >>> api/location/888
    {
      "id": 888,
      "name": "University of Toronto"
    }

    
## Get events by location

Api call:

    api/location/<location id>/events/<lim>

  `location id` - The id of the location

  `lim` - max number of events to return, max 25

Example return:

    >>> api/location/888/events/2
    {
      "events": [
        {
          "author_id": 1,
          "body": "ou",
          "id": 1,
          "location_id": 888,
          "name": "New event 1",
          "place": "auaoenu",
          "serving": "Pizza!",
          "time": "Wed, 21 Feb 1900 15:37:00 GMT",
          "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
        },
        {
          "author_id": 1,
          "body": "'''",
          "id": 2,
          "location_id": 888,
          "name": "aoeue",
          "place": "uuuu",
          "serving": "Pizza!",
          "time": "Wed, 21 Feb 1900 15:37:00 GMT",
          "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
        }
      ]
    }

## Get users by location

API call:

    api/location/<location id>/users/<lim>

  `location id` - The id of the location

  `lim` - Max number of events to return, max 25

Example return:

    >>> api/location/888/users/3
    {
      "users": [
        {
          "email": "a@b.com",
          "id": 1,
          "location_id": 888,
          "member_since": "Sat, 21 Feb 2015 20:15:49 GMT"
        },
        {
          "email": "b@c.com",
          "id": 2,
          "location_id": 888,
          "member_since": "Sat, 21 Feb 2015 21:35:26 GMT"
        },
        {
          "email": "a@a.com",
          "id": 3,
          "location_id": 888,
          "member_since": "Sat, 21 Feb 2015 21:35:26 GMT"
        }
      ]
    }

# Users

## Get user profile

API call:

    api/user/<user id>


  `user id` - The user's id

Example return:

    >>> api/user/1  
    {
      "email": "a@b.com",
      "id": 1,
      "location_id": 888,
      "member_since": "Sat, 21 Feb 2015 20:15:49 GMT",
      "num_events_attended": 5,
      "num_events_created": 5
    }

## Get user's created events

API call:

    api/user/<user id>/events/<lim>

  `user id` - The id of the user's 

  `lim` - Max number of events to return, max 25

{
  "events": [
    {
      "author_id": 1,
      "body": "ou",
      "id": 1,
      "location_id": 888,
      "name": "New event 1",
      "place": "auaoenu",
      "serving": "Pizza!",
      "time": "Wed, 21 Feb 1900 15:37:00 GMT",
      "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
    },
    {
      "author_id": 1,
      "body": "'''",
      "id": 2,
      "location_id": 888,
      "name": "aoeue",
      "place": "uuuu",
      "serving": "Pizza!",
      "time": "Wed, 21 Feb 1900 15:37:00 GMT",
      "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
    }
  ]
}

## Get user's attended events

API call:

    api/user/<user id>/events/<lim>

  `user id` - The id of the user's 

  `lim` - Max number of events to return, max 25

Example return:

    {
      "events": [
        {
          "author_id": 1,
          "body": "ou",
          "id": 1,
          "location_id": 888,
          "name": "New event 1",
          "place": "auaoenu",
          "serving": "Pizza!",
          "time": "Wed, 21 Feb 1900 15:37:00 GMT",
          "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
        },
        {
          "author_id": 1,
          "body": "'''",
          "id": 2,
          "location_id": 888,
          "name": "aoeue",
          "place": "uuuu",
          "serving": "Pizza!",
          "time": "Wed, 21 Feb 1900 15:37:00 GMT",
          "timestamp": "Sat, 21 Feb 2015 20:37:05 GMT"
        }
      ]
    }
