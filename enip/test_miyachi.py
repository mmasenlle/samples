import contextlib,time
from cpppo.server.enip.get_attribute import proxy_simple as device
import cpppo.server.enip.poll


def loop( via, **kwds ):
    with via: # ensure via.close_gateway invoked on any Exception
        with contextlib.closing( cpppo.server.enip.poll.execute( via, **kwds )) as executor:
            # PyPy compatibility; avoid deferred destruction of generators
            results		= list( executor )
            return results[0][1]

R_tag=[('@0xA2/0x0014/0x05','REAL')]
I_tag=[('@0xA2/0x0411/0x05','REAL')]
def I_tag_set(amps):
    return [('@0xA2/0x0411/0x05=(REAL)'+str(amps),'REAL')]


#via = device(host="200.200.200.51", port=44818 )
via	= device(host="172.24.1.51", port=44818 )

print 'Resistencia:',loop(via, params=R_tag)
I1=loop(via, params=I_tag)[0]
print 'Intensidad: ',I1
I2=I1+10.0

R_media=0.0
RR=[]
N=10


while True:
    time.sleep( .5 )
    try:
        R=loop(via, params=R_tag)[0]
        print 'R['+str(len(RR))+']:',R
        R_media+=R
        RR.append(R)
        if len(RR) >= N:
            R_media=R_media/len(RR)
            I=loop(via, params=I_tag)[0]
            print 'I:',I
            print 'R_media:',R_media
            # ajustar intensidad en funcion de R media
            if I==I1: print 'I:='+str(I2)+' :',loop(via, params=I_tag_set(I2))
            else: print 'I:='+str(I1)+' :',loop(via, params=I_tag_set(I1))
            print 'I:',loop(via, params=I_tag)[0]
            RR=[]
            R_media=.0
    except Exception as exc:
        print 'Error:',exc

