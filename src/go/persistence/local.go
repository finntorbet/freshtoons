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
			users[i] = user
			userUpdated = true
			break
		}
	}

	if !userUpdated {
		users = append(users, user)
	}

	// Marshal with indentation for pretty-printing
	jsonData, err := json.MarshalIndent(users, "", "    ") // 4-space indentation
	if err != nil {
		return err
	}

	// Write to file
	err = os.WriteFile(lf.FilePath, jsonData, 0644)
	if err != nil {
		return err
	}

	return nil
}
