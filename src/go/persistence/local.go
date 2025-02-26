package persistence

import (
	"encoding/json"
	"errors"
	"os"
)

type LocalFile struct {
	FilePath string
}

func (lf *LocalFile) GetUsers() ([]User, error) {
	file, err := os.Open(lf.FilePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var users []User
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&users); err != nil {
		return nil, err
	}

	return users, nil
}

func (lf *LocalFile) SaveUser(user User) error {
	users, err := lf.GetUsers()
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		return err
	}

	userUpdated := false
	for i, u := range users {
		if u.UserID == user.UserID {
			users[i] = user // Update existing user
			userUpdated = true
			break
		}
	}

	if !userUpdated {
		users = append(users, user) // Add new user if not found
	}

	file, err := os.Create(lf.FilePath)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	return encoder.Encode(users)
}
