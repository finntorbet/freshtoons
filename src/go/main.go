package main

import (
	"fmt"
	"freshtoons/persistence"
)

const (
	TokenURL   = "https://accounts.spotify.com/api/token"
	BaseAPIURL = "https://api.spotify.com/v1"
)

func main() {
	storage := &persistence.LocalFile{FilePath: "users.json"}

	users, err := storage.GetUsers()
	if err != nil {
		fmt.Println("Error retrieving users:", err)
		return
	}
	user_to_update := users[0]

	user := persistence.User{
		AccessToken:  "example_access_token",
		RefreshToken: "example_refresh_token",
		PlaylistID:   "playlist123",
		UserID:       "user123",
		PlaylistSize: 50,
	}

	err = storage.SaveUser(user)
	if err != nil {
		fmt.Println("Error saving user:", err)
		return
	}

	user_to_update.AccessToken = "NEW_TOKEN"
	err = storage.SaveUser(user_to_update)
	if err != nil {
		fmt.Println("Error saving user:", err)
		return
	}

	users, err = storage.GetUsers()
	if err != nil {
		fmt.Println("Error retrieving users:", err)
		return
	}

	fmt.Println("Stored Users:", users)
}
