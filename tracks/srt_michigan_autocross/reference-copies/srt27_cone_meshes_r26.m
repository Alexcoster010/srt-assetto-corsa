function M=srt27_cone_meshes_r26(C)
% Build fixed cone scenery in reduced vehicle coordinates: x forward,
% y left, z up. The renderer performs the sole y-left to Unreal y-right
% reflection after all source geometry has been converted to this frame.
required={'id','role','position_xz_m','height_m','base_width_m','tip_heading_rad'};
assert(isfield(C,'cones')&&isstruct(C.cones)&&numel(C.cones)==137, ...
    'r26:UnexpectedConeInventory','The r26 scene requires all 137 r25b cones.');
M=struct('upright_body',empty_mesh(),'upright_base',empty_mesh(), ...
    'pointer_body',empty_mesh(),'pointer_base',empty_mesh());
for k=1:numel(C.cones)
    c=C.cones(k);
    assert(all(isfield(c,required)),'r26:IncompleteConeVisual', ...
        'Cone %d lacks required visual geometry.',k);
    role=char(c.role);assert(any(strcmp(role,{'upright','pointer'})), ...
        'r26:InvalidConeRole','Cone %s has invalid role %s.',char(c.id),role);
    q=double(c.position_xz_m(:)');h=double(c.height_m);b=double(c.base_width_m);
    heading=double(c.tip_heading_rad);
    assert(numel(q)==2&&all(isfinite(q))&&isfinite(h)&&isfinite(b)&&h>b/2&&b>0&&isfinite(heading), ...
        'r26:InvalidConeVisual','Cone %s has invalid visual geometry.',char(c.id));
    % Source native [X,Z-right] becomes reduced vehicle [x,y-left].
    xy=q.*[1 -1];t=.02;
    if strcmp(role,'upright')
        p=[xy t];tip=[xy h];axes=eye(3);center=[xy t/2];dims=[b b t];
    else
        % Native heading [cos(theta),sin(theta) Z-right] becomes y-left.
        d=[cos(heading) -sin(heading) 0];up=[0 0 1];side=cross(d,up);
        p=[xy b/2];tip=[xy 0]+sqrt(h*h-b*b/4)*d;
        axes=[d' up' side'];center=p;dims=[t b b];
    end
    [vb,fb]=box_mesh(center,axes,dims);
    [vo,fo]=cone_mesh(p,tip,b);
    M.([role '_base'])=append_mesh(M.([role '_base']),vb,fb);
    M.([role '_body'])=append_mesh(M.([role '_body']),vo,fo);
end
end

function m=empty_mesh()
m=struct('vertices',zeros(0,3),'faces',zeros(0,3));
end

function m=append_mesh(m,v,f)
m.faces=[m.faces;f+size(m.vertices,1)];
m.vertices=[m.vertices;v];
end

function [v,f]=cone_mesh(p,tip,width)
axisVector=(tip-p)/norm(tip-p);ref=[0 0 1];
if abs(dot(axisVector,ref))>.9,ref=[1 0 0];end
u=cross(ref,axisVector);u=u/norm(u);vside=cross(axisVector,u);
angle=(0:23)'*2*pi/24;
v=[p+.30*width*(cos(angle)*u+sin(angle)*vside);p;tip];
f=zeros(48,3);for j=1:24,n=mod(j,24)+1;f(2*j-1,:)=[j-1 n-1 25];f(2*j,:)=[24 n-1 j-1];end
end

function [v,f]=box_mesh(center,axes,dims)
assert(abs(det(axes)-1)<1e-9,'r26:MirroredMesh','Cone frame must be right handed.');
v=[-1 -1 -1;1 -1 -1;1 1 -1;-1 1 -1;-1 -1 1;1 -1 1;1 1 1;-1 1 1].*(dims/2);
v=center+v*axes';
f=[0 2 1;0 3 2;4 5 6;4 6 7;0 1 5;0 5 4;3 7 6;3 6 2;0 4 7;0 7 3;1 2 6;1 6 5];
end
