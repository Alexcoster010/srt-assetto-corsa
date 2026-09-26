function H=srt27_human_course_r26
% Preserved event path plus a synthetic user-requested closed-course return.
root=fileparts(mfilename('fullpath'));folder=fullfile(root,'live-driving','autocross-r26');
if ~isfolder(folder),mkdir(folder);end
source=fullfile(root,'autocross-cones-r25b','course-r25b.json');
copy=fullfile(folder,'course-reference.json');
if ~isfile(copy),copyfile(source,copy);end
assert(strcmp(sha(source),sha(copy)),'r26:SourceChanged','Preserved course differs from source; create a revision before updating.');
C=jsondecode(fileread(copy));
for i=1:numel(C.cones),C.cones(i).position_xz_m=C.cones(i).position_xz_m(:)';end
q=double(C.driving_path_xz_m).*[1 -1];
original_s=[0;cumsum(vecnorm(diff(q),2,2))];
[return_path,connector]=srt27_closed_course_connector_r26(q);
closed_path=[q;return_path(2:end,:)];
s=[0;cumsum(vecnorm(diff(closed_path),2,2))];
heading=unwrap(atan2(gradient(closed_path(:,2),s),gradient(closed_path(:,1),s)));
H=struct('path_xy_m',closed_path,'s_m',s,'curvature_per_m',gradient(heading,s),...
    'initial_state_xy_yaw',[q(1,:) atan2(q(2,2)-q(1,2),q(2,1)-q(1,1))],...
    'C',C,'folder',folder,'source_sha256',sha(copy),...
    'coordinate_note','Native [X,Yup,Zright] -> reduced [X,-Z,Yup]; renderer reflects reduced-left to Unreal-right once.',...
    'closed_course',true,'cone_count',numel(C.cones),...
    'original_path_xy_m',q,'original_finish_s_m',original_s(end),...
    'return_path_xy_m',return_path,'return_path_metadata',connector,...
    'return_path_label','Synthetic user-requested connector; not part of the real event course.',...
    'return_path_is_real_event_course',false);
assert(H.cone_count==137&&all(diff(s)>0)&&abs(H.initial_state_xy_yaw(3))<1e-6);
assert(isequal(q.*[1 -1],double(C.driving_path_xz_m)),'Coordinate round trip failed.');
assert(isequal(H.path_xy_m(1,:),H.path_xy_m(end,:)),'r26:Closure','Closed route must end exactly at its first point.');
assert(isequal(H.path_xy_m(1:size(q,1),:),q),'r26:OriginalPathChanged','The event path must remain an exact prefix.');
end
function value=sha(p)
f=fopen(p,'rb');assert(f>0);c=onCleanup(@()fclose(f));b=fread(f,Inf,'*uint8');d=java.security.MessageDigest.getInstance('SHA-256');d.update(b);value=lower(reshape(dec2hex(typecast(d.digest(),'uint8'),2)',1,[]));
end
