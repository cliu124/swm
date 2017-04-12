## RIGHT HAND SIDE OF THE EQUATIONS
def rhs(u,v,h):
    """ Set of equations:
    
    u_t = qhv - p_x + Fx + Mx(u,v) - bottom_friction
    v_t = -qhu - p_y + My(u,v)  - bottom_friction
    h_t = -(uh)_x - (vh)_y
    
    with p = .5*(u**2 + v**2) + gh, the bernoulli potential
    and q = (v_x - u_y + f)/h the potential vorticity
    
    using the enstrophy and energy conserving scheme (Arakawa and Lamb, 1981) and
    a biharmonic lateral mixing term based on Shchepetkin and O'Brien (1996).
    """
    
    #TODO param[nu_B] is large, applying the biharmonic creates tiny values (as dx^4 is large)
    #TODO think about a way to avoid possibly involved rounding errors especially with single precision
    #TODO might be efficiently only possible for dx=dy
    
    h_u = ITu.dot(h)    # h on u-grid
    h_v = ITv.dot(h)    # h on v-grid    
    h_q = ITq.dot(h)    # h on q-grid
    
    U = u*h_u    # volume fluxes: U on u-grid
    V = v*h_v    # and V on v-grid
    
    KE = IuT.dot(u**2) + IvT.dot(v**2)  # kinetic energy without .5-factor
    
    q = (f_q + Gvx.dot(v) - Guy.dot(u)) / h_q       # potential vorticity q
    p = .5*KE + param['g']*h            # Bernoulli potential p
    
    ## BOTTOM FRICTION: quadratic drag
    sqrtKE = np.sqrt(KE)
    bfric_u = param['c_D']/param['H']*ITu.dot(sqrtKE)*u
    bfric_v = param['c_D']/param['H']*ITv.dot(sqrtKE)*v
    
    ## ADVECTION
    # Sadourny, 1975 enstrophy conserving scheme.
    #adv_u = Iqu.dot(q)*Ivu.dot(V)
    #adv_v = -Iqv.dot(q)*Iuv.dot(U)
    
    # Arakawa and Lamb, 1981
    adv_u, adv_v = ALadvection(q,U,V)
    
    ## LATERAL MIXING OPERATOR
    # crude but simple bi-harmonic mixing
    #bidiff_u = param['nu_B']*LLu.dot(u)
    #bidiff_v = param['nu_B']*LLv.dot(v)                      
    
    # symmetric stress tensor S = (S11, S12, S12, -S11), store only S11, S12
    S = (Gux.dot(u)-Gvy.dot(v),G2vx.dot(v) + G2uy.dot(u))
    hS = (h*S[0],h_q*S[1])

    diff_u = (GTx.dot(hS[0]) + Gqy.dot(hS[1])) / h_u
    diff_v = (Gqx.dot(hS[1]) - GTy.dot(hS[0])) / h_v

    # biharmonic stress tensor R = (R11, R12, R12, -R11), store only R11, R12
    R = (Gux.dot(diff_u) - Gvy.dot(diff_v), G2vx.dot(diff_v) + G2uy.dot(diff_u))
    hR = (h*R[0],h_q*R[1])
    
    bidiff_u = param['nu_B']*(GTx.dot(hR[0]) + Gqy.dot(hR[1])) / h_u
    bidiff_v = param['nu_B']*(Gqx.dot(hR[1]) - GTy.dot(hR[0])) / h_v
    
    ## RIGHT-HAND SIDE: ADD TERMS
    rhs_u = adv_u - GTx.dot(p) + Fx - bidiff_u - bfric_u
    rhs_v = adv_v - GTy.dot(p) - bidiff_v - bfric_v
    rhs_h = -Gux.dot(U) - Gvy.dot(V)
    
    return rhs_u, rhs_v, rhs_h

def ALadvection(q,U,V):
    """ Arakawa and Lamb,1981 advection terms. See interpolation.py for further information. """
    
    AL1q = AL1.dot(q)
    AL2q = AL2.dot(q)
    
    adv_u = Seur.dot(ALeur.dot(q)*U) + Seul.dot(ALeul.dot(q)*U) +\
            Sau.dot(AL1q[indx_au]*V) + Sbu.dot(AL2q[indx_bu]*V) +\
            Scu.dot(AL2q[indx_cu]*V) + Sdu.dot(AL1q[indx_du]*V)

    adv_v = Spvu.dot(ALpvu.dot(q)*V) + Spvd.dot(ALpvd.dot(q)*V) -\
            Sav.dot(AL1q[indx_av]*U) - Sbv.dot(AL2q[indx_bv]*U) -\
            Scv.dot(AL2q[indx_cv]*U) - Sdv.dot(AL1q[indx_dv]*U)
    
    return adv_u, adv_v