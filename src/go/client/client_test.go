package spotify

import (
	"fmt"
	"freshtoons/persistence"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetLikedSongs(t *testing.T) {

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != LikedSongsURL {
			t.Errorf("Expected to request '%s', got: %s", LikedSongsURL, r.URL.Path)
		}
		if r.PostForm.Get("limit") == "10" {
			t.Errorf("Expected Accept: application/json header, got: %s", r.Header.Get("Accept"))
		}
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(
			`{
			"items": [
				{ "track": { "id": "track1" } },
				{ "track": { "id": "track2" } }
			]
		}`))
	}))
	defer server.Close()

	client := NewSpotifyClient("CLIENT_B64", server.URL, server.URL)
	trackIDs, err := client.GetLikedSongs("test_token", 10)

	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(trackIDs) != 2 {
		t.Errorf("Expected 2 track IDs, got %d", len(trackIDs))
	}
	if trackIDs[0] != "track1" || trackIDs[1] != "track2" {
		t.Errorf("Unexpected track IDs: %v", trackIDs)
	}
}

func TestGetNewToken(t *testing.T) {

	tokenUrlPath := "/api/token"
	oldAccessToken := "an_access_token"
	newAccessToken := "a_new_access_token"
	oldRefreshToken := "a_refresh_token"
	newRefreshToken := "a_new_refresh_token"

	user := persistence.User{
		AccessToken:  oldAccessToken,
		RefreshToken: oldRefreshToken,
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != tokenUrlPath {
			t.Errorf("Expected to request '%s', got: %s", LikedSongsURL, r.URL.Path)
		}
		body, err := io.ReadAll(r.Body)
		if err != nil {
			t.Errorf("Error in test code reading body!")
		}
		fmt.Println(body)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(
			`{
			"access_token": "` + oldAccessToken + `",
			"refresh_token": "` + oldRefreshToken + `",
		}`))
	}))
	defer server.Close()

	client := NewSpotifyClient("CLIENT_B64", server.URL, server.URL+tokenUrlPath)
	err := client.GetNewToken(&user)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if user.AccessToken != newAccessToken {
		t.Errorf("Expected new access token (%s) but got: %s", newAccessToken, user.AccessToken)
	}
	if user.RefreshToken != newRefreshToken {
		t.Errorf("Expected new access token (%s) but got: %s", newAccessToken, user.AccessToken)
	}
}
