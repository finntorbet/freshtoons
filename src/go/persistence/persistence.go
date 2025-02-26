package persistence

type User struct {
	AccessToken  string
	RefreshToken string
	PlaylistID   string
	UserID       string
	PlaylistSize int
}

type Persistence interface {
	GetUsers() ([]User, error)
	SaveUser(user User) error
}
