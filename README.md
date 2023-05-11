# Freshtoons
This repository represents a project to create and update a playlist with a Spotify user's top *n* songs from their *Liked Songs* library, allowing the most recent songs to be liked by the user to be listened to with the common shuffle feature of multimedia software. Refer to User Pain Outlined below for more on the project's motivation.

### User Pain Outlined
As a Spotiy user who uses the *like* feature frequently to make note of songs I enjoy, I found it frustrating that I couldn't listen to a collection of the most recent songs I liked without having to linearly play the songs in the order they appear in the Liked Songs library (as using shuffle would shuffle all songs in the library which is usually a substantial number of elements). 

A program that could create and refresh daily a given playlist with the most recent songs would create a low-effort solution to this User Pain.

## Architecture and Design
The frequency for updating the playlist is decided to be daily. As the code only needs to run once every 24 hours, there is no need for constantly provisioning hardware, as such serverless is the best course of action. Since the team has the most experience with AWS, Lambda seemed like the best fit.

To speed up development, a CI/CD pipeline will be constructed to quickly get code into the staging environment (since there is only one user as of now, staging and production will be the same). GitHub Actions provides a serverless pipeline where the deployment script is neatly included and invoked from the code repository itself, requiring very little extra setup.

___
###### Non Functional Side Note
- AWS Lambda provides 1 million free calls in its free tier. 
- GitHub Actions is free for public repositories. 

Both these choices provide the program with a cost-effective solution to the architecture, a key non-functional constraint. 
___

## Implementation
Spotify API is the key external dependency for this project. The following urls are used (the links take you to their documentation).
- [https://accounts.spotify.com/api/token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow)
- [https://api.spotify.com/v1/users/USER_ID/playlists](https://developer.spotify.com/documentation/web-api/reference/create-playlist)
- [https://api.spotify.com/v1/me/playlists](https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists)
- [https://api.spotify.com/v1/me/tracks](https://developer.spotify.com/documentation/web-api/reference/save-tracks-user)
- [https://api.spotify.com/v1/playlists/PLAYLIST_ID/tracks](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks)

A main concern for the program is how to obtain an authorization token for a user. For that the following [example](https://github.com/spotify/web-api-examples/tree/master/authentication) was used locally to gain initial token for the current sole user. The scope of this project would like to be extended to cover a frontend that can perform the authorization flow between Spotify and itself, then store the new user's authorization details within the S3 datastore. This would open up the program to be used by anyone who can access the frontend and add their users details in.

#### Data Security
To keep deployment information hidden and secure, GitHub Action Secrets is used to keep the AWS sensitive keys hidden whilst keeping the deployment workflow in the public *.github* and parametrised.

To secure the spotify authorization token, the data will be stored in a private S3 bucket as a csv since the data does not need to be secure or highly accessible.

##To Do
The following elements are outlined in descending order of priority-effort (the higher the item the more impact it will have with the least amount of effort).
- Complete outstanding happy path unit tests.
- Buff out current unit tests with chaos engineering to catch edge cases and fail situations.
- Create frontend for Spotify authorization of new users.
  - Create new playlist and populate it upon successful authorization. 
  - Insert new token information in S3 for daily refresh.
- Create smoke tests for backend system for end-to-end mock.
- Add feature to update the playlist with liked songs from the past *n* days instead of just the top *n*.
___
######Note
This section should be moved to GitHub Issues within the code repository to keep project management tidy and tied to branch/PR operations.
___