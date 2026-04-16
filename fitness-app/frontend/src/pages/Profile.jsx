import React from 'react';
const Profile = ({ user }) => <div className="p-8"><h1 className="text-2xl font-bold">Профиль</h1><p className="mt-4">Email: {user?.email}</p></div>;
export default Profile;
