
package httpapi.authz

# bob is alice's manager, and betty is charlie's.
subordinates := {"alice": [], "charlie": [], "bob": ["alice"], "betty": ["charlie"]}

default allow := false

# Allow users to get their own salaries.
allow {
input.method == "GET"
input.path == ["finance", "salary", input.user]
}

# Allow managers to get their subordinates' salaries.
allow {
some username
input.method == "GET"
input.path = ["finance", "salary", username]
subordinates[input.user][_] == username
}

# Allow HR members to get anyone's salary.
allow {
input.method == "GET"
input.path = ["finance", "salary", _]
input.user == hr[_]
}

# Allow super admins to perform any action.
allow {
input.user == super_admin[_]
}

hr := [
"HR_GOD",
"Miguel",
]

super_admin := [
"pedro",
"Jonas",
"schmitt"
]
