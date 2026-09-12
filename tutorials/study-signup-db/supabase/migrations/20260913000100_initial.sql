-- 연습용 데이터만 사용한다. 사용자 식별자는 Auth가 발급한다.
create table public.events (
  id uuid primary key default gen_random_uuid(),
  title text not null check (length(trim(title)) > 0),
  capacity integer not null check (capacity > 0),
  registered_count integer not null default 0
    check (registered_count >= 0 and registered_count <= capacity)
);
create table public.registrations (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id),
  user_id uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  unique (event_id, user_id)
);
create index registrations_user_idx on public.registrations(user_id);
alter table public.events enable row level security;
alter table public.registrations enable row level security;
revoke all on public.events, public.registrations from anon, authenticated;
grant select on public.events to authenticated;
grant select, insert, delete on public.registrations to authenticated;
create policy events_read on public.events for select to authenticated using (true);
create policy registrations_read on public.registrations for select to authenticated
  using ((select auth.uid()) = user_id);
create policy registrations_insert on public.registrations for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy registrations_delete on public.registrations for delete to authenticated
  using ((select auth.uid()) = user_id);
-- 같은 모임의 행을 UPDATE하며 잠근다. 실패한 INSERT와 카운터 변경은 함께 취소된다.
create function public.adjust_seats() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if TG_OP = 'INSERT' then
    update public.events set registered_count = registered_count + 1
      where id = NEW.event_id and registered_count < capacity;
    if not found then
      if not exists (select 1 from public.events where id = NEW.event_id) then
        raise exception '모임이 없습니다' using errcode = '23503';
      end if;
      raise exception '정원이 찼습니다' using errcode = '23514';
    end if;
    return NEW;
  end if;
  update public.events set registered_count = registered_count - 1 where id = OLD.event_id;
  return OLD;
end;
$$;
revoke all on function public.adjust_seats() from public, anon, authenticated;
create trigger registrations_seats_insert before insert on public.registrations
  for each row execute function public.adjust_seats();
create trigger registrations_seats_delete after delete on public.registrations
  for each row execute function public.adjust_seats();
-- 브라우저가 다른 사용자의 ID를 보내지 않아도 되는 신청 경로.
create function public.register_for_event(target_event uuid) returns public.registrations
language plpgsql security invoker set search_path = '' as $$
declare result public.registrations;
begin
  if auth.uid() is null then raise exception '로그인이 필요합니다' using errcode = '42501'; end if;
  insert into public.registrations(event_id, user_id) values (target_event, auth.uid()) returning * into result;
  return result;
end;
$$;
revoke all on function public.register_for_event(uuid) from public, anon;
grant execute on function public.register_for_event(uuid) to authenticated;
