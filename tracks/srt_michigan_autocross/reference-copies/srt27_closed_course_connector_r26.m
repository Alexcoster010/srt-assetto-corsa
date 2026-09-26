function [P,metadata]=srt27_closed_course_connector_r26(original_path_xy_m)
% Smooth exterior connector from the r26 finish back to its original start.
% This geometry is synthetic and user-requested. It is not a real event course.
validateattributes(original_path_xy_m,{'numeric'},{'2d','ncols',2,'finite','real'});
assert(size(original_path_xy_m,1)>=3,'r26:OriginalPath','Original path is too short.');

start=original_path_xy_m(1,:);
finish=original_path_xy_m(end,:);
start_tangent=unit(original_path_xy_m(2,:)-start);
finish_tangent=unit(finish-original_path_xy_m(end-1,:));
assert(dot(start_tangent,[1 0])>.999&&dot(finish_tangent,[-1 0])>.999,...
    'r26:EndpointHeading','The synthetic connector is specific to the preserved r26 endpoint headings.');

step_m=.15;
radius_m=30;
approach_length_m=20;
approach=start-approach_length_m*start_tangent;
left_normal=[-start_tangent(2) start_tangent(1)];
circle_center=approach-radius_m*left_normal;
entry=circle_center-radius_m*left_normal;

% The departure Bezier continues the westbound finish tangent, eases below
% the event-course envelope, and meets the 30 m turnaround almost G2.
c0=finish;
c1=finish+25*finish_tangent;
c3=entry;
c2=entry-26.1*finish_tangent;
control=[c0;c1;c2;c3];
n_bezier=max(2,ceil(sum(vecnorm(diff(control),2,2))/step_m)+1);
t=linspace(0,1,n_bezier)';
A=(1-t).^3.*c0+3*(1-t).^2.*t.*c1+3*(1-t).*t.^2.*c2+t.^3.*c3;

% Clockwise half-circle: westbound at entry and eastbound at approach.
n_turn=max(2,ceil(pi*radius_m/step_m)+1);
theta=linspace(-pi/2,-3*pi/2,n_turn)';
B=circle_center+radius_m*(cos(theta).*start_tangent+sin(theta).*left_normal);
n_approach=max(2,ceil(norm(start-approach)/step_m)+1);
u=linspace(0,1,n_approach)';
C=approach+(start-approach).*u;

P=[A;B(2:end,:);C(2:end,:)];
P(1,:)=finish;
P(end,:)=start;
metadata=struct(...
    'label','Synthetic user-requested connector; not part of the real event course.',...
    'is_real_event_course',false,...
    'sample_step_target_m',step_m,...
    'turnaround_radius_m',radius_m,...
    'departure_bezier_control_xy_m',control,...
    'turnaround_center_xy_m',circle_center,...
    'turnaround_entry_xy_m',entry,...
    'start_approach_xy_m',approach);
end

function v=unit(v)
v=v/norm(v);
end
