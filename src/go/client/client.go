package spotify

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"freshtoons/persistence"
	"io"
	"net/http"
)

// Variable instead of const to allow ease of mocking
const (
	LikedSongsURL     = "/me/tracks"
	PlaylistsURL      = "/playlists"
	UserPlaylistsURL  = "/me/playlists"
	CreatePlaylistURL = "/users/%s/playlists"
)

// SpotifyClient handles API interactions
type SpotifyClient struct {
	BaseUrl    string // Included in struct to allow ease of mocking
	TokenUrl   string // Included in struct to allow ease of mocking
	HTTPClient *http.Client
	AuthHeader string
}

// NewSpotifyClient initializes the client with a Base64-encoded client_id:client_secret
func NewSpotifyClient(encodedAuth string, baseUrl string, tokenUrl string) *SpotifyClient {
	return &SpotifyClient{
		HTTPClient: &http.Client{},
		AuthHeader: "Basic " + encodedAuth,
		BaseUrl:    baseUrl,
		TokenUrl:   tokenUrl,
	}
}

func mapToReader(m map[string]interface{}) io.Reader {
	b, _ := json.Marshal(m)
	return bytes.NewReader(b)
}

func (s *SpotifyClient) GetNewToken(user *persistence.User) error {

	payload := map[string]interface{}{
		"grant_type":    "refresh_token",
		"refresh_token": user.RefreshToken,
	}

	req, err := http.NewRequest("POST", s.TokenUrl, mapToReader(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", s.AuthHeader)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return errors.New("failed to get new token")
	}

	var result struct {
		AccessToken  string `json:"access_token"`
		RefreshToken string `json:"refresh_token"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return err
	}

	// Update the user's access token
	user.AccessToken = result.AccessToken
	user.RefreshToken = result.RefreshToken
	return nil
}

// GetLikedSongs fetches the user's liked songs
func (s *SpotifyClient) GetLikedSongs(accessToken string, limit int) ([]string, error) {
	// Ensure limit is within Spotify's accepted range (1-50)
	if limit <= 0 || limit > 50 {
		limit = 50
	}

	endpoint := fmt.Sprintf("%s%s?limit=%d", s.BaseUrl, LikedSongsURL, limit)

	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+accessToken)

	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, errors.New(fmt.Sprintf("failed to fetch liked songs %v", resp.StatusCode))
	}

	var response struct {
		Items []struct {
			Track struct {
				ID string `json:"id"`
			} `json:"track"`
		} `json:"items"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	var trackIDs []string
	for _, item := range response.Items {
		trackIDs = append(trackIDs, item.Track.ID)
	}

	return trackIDs, nil
}

// UpdatePlaylist updates a given playlist with new track URIs
func (s *SpotifyClient) UpdatePlaylist(accessToken string, playlistID string, trackURIs []string) error {
	updateData := map[string]interface{}{
		"uris": trackURIs,
	}

	body, err := json.Marshal(updateData)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("PUT", fmt.Sprintf("%s%s/%s/tracks", s.BaseUrl, PlaylistsURL, playlistID), bytes.NewBuffer(body))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return errors.New("failed to update playlist")
	}

	return nil
}

// PlaylistExists checks if a playlist exists
func (s *SpotifyClient) PlaylistExists(accessToken string, playlistID string) (bool, error) {
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/%s", PlaylistsURL, playlistID), nil)
	if err != nil {
		return false, err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)

	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return false, nil
	}
	if resp.StatusCode != http.StatusOK {
		return false, errors.New("error checking playlist existence")
	}

	return true, nil
}

// CreatePlaylist creates a new playlist for the user
func (s *SpotifyClient) CreatePlaylist(accessToken string, userID, name, description string, isPublic bool) (string, error) {
	playlistData := map[string]interface{}{
		"name":        name,
		"description": description,
		"public":      isPublic,
	}

	body, err := json.Marshal(playlistData)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", fmt.Sprintf(CreatePlaylistURL, userID), bytes.NewBuffer(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return "", errors.New("failed to create playlist")
	}

	var result struct {
		ID string `json:"id"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	return result.ID, nil
}
