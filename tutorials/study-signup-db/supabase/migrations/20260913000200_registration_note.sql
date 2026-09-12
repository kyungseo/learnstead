-- 기존 신청을 남긴 채 선택 메모를 추가한다. 기존 행에는 빈 문자열이 들어간다.
alter table public.registrations add column note text not null default '' check (length(note) <= 200);
grant update(note) on public.registrations to authenticated;
create policy registrations_update on public.registrations for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
