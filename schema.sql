create table
  public.playlist (
    playlist_id bigint generated by default as identity not null,
    user_id bigint null,
    playlist_name text null,
    created_at timestamp with time zone not null default now(),
    constraint playlist_pkey primary key (playlist_id),
    constraint playlist_playlist_id_key unique (playlist_id)
  ) tablespace pg_default;

create table
  public.playlist_collaborator (
    id bigint generated by default as identity not null,
    playlist_id bigint not null,
    user_id bigint not null,
    created_at timestamp with time zone not null default now(),
    constraint playlist_contributor_pkey primary key (id),
    constraint playlist_contributor_id_key unique (id)
  ) tablespace pg_default;

create table
  public.playlist_song (
    id bigint generated by default as identity not null,
    song_id bigint not null,
    playlist_id bigint not null,
    created_at timestamp with time zone not null default now(),
    constraint playlist_song_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.user (
    user_id bigint generated by default as identity not null,
    first_name text null,
    last_name text null,
    created_at timestamp with time zone not null default now(),
    constraint user_pkey primary key (user_id),
    constraint user_user_id_key unique (user_id)
  ) tablespace pg_default;
