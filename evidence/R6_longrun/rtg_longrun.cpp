#include <bits/stdc++.h>
using namespace std;
struct Res{double bad_all,bad_late,H_early,H_late,coverage,maxshare,Gnorm,Hpre,Hpost1,Hpost5;};

double urand(mt19937_64 &g){return uniform_real_distribution<double>(0.0,1.0)(g);} 
double nrand(mt19937_64 &g){return normal_distribution<double>(0.0,1.0)(g);} 

Res sim(int seed,int T,int mode){
    const int N=32,D=12,OD=5;
    mt19937_64 rng(seed);
    vector<vector<int>> allowed(N, vector<int>(N,0));
    int offs[7]={1,3,7,11,17,23,29}; int shift=seed%7;
    for(int i=0;i<N;i++){
        int used=0,k=0; while(used<OD){int j=(i+offs[(k+shift)%7])%N; if(j!=i && !allowed[i][j]){allowed[i][j]=1;used++;}k++;}
    }
    vector<vector<array<double,D>>> phi(N, vector<array<double,D>>(N));
    for(int i=0;i<N;i++)for(int j=0;j<N;j++){
        double norm=0; for(int z=0;z<D;z++){phi[i][j][z]=nrand(rng);norm+=phi[i][j][z]*phi[i][j][z];}
        norm=sqrt(norm)+1e-12; for(int z=0;z<D;z++)phi[i][j][z]/=norm;
    }
    vector<vector<double>> base(N,vector<double>(N)), G(N,vector<double>(N,0.0));
    vector<array<double,D>> M(N); for(auto &a:M) for(double &v:a)v=0;
    for(int i=0;i<N;i++)for(int j=0;j<N;j++)base[i][j]=(allowed[i][j]?2.8:-4.2)+0.25*nrand(rng);
    int x=rng()%N; int q=max(1,T/10); long long badAll=0,badLate=0; double HE=0,HL=0; vector<int> counts(N,0);
    int shocks[3]={T/4,T/2,3*T/4}; double pre[3]={0},p1[3]={0},p5[3]={0};int npre[3]={0},np1[3]={0},np5[3]={0};
    vector<double> logits(N),p(N),scores(N),prop(N); array<double,D> gv{};
    for(int t=0;t<T;t++){
        for(int si=0;si<3;si++) if(t==shocks[si]){
            vector<vector<double>> noise(N,vector<double>(N)); double norm=0;
            for(int r=0;r<N;r++){double mu=0;for(int c=0;c<N;c++){noise[r][c]=nrand(rng);mu+=noise[r][c];}mu/=N;for(int c=0;c<N;c++){noise[r][c]-=mu;norm+=noise[r][c]*noise[r][c];}}
            norm=sqrt(norm)+1e-12; for(int r=0;r<N;r++)for(int c=0;c<N;c++)G[r][c]+=40.0*noise[r][c]/norm;
        }
        double mx=-1e300; for(int j=0;j<N;j++){logits[j]=base[x][j]+G[x][j]; if((mode==1||mode==2)&&!allowed[x][j])logits[j]=-1e100; mx=max(mx,logits[j]);}
        double s=0;for(int j=0;j<N;j++){p[j]=exp(logits[j]-mx);s+=p[j];}for(double &v:p)v/=s;
        double sumA=0;for(int j=0;j<N;j++)if(allowed[x][j])sumA+=p[j]; double H=0;for(int j=0;j<N;j++)if(allowed[x][j]){double v=p[j]/sumA;if(v>0)H-=v*log(v);}
        if(t<q)HE+=H; if(t>=T-q)HL+=H;
        for(int si=0;si<3;si++){int ss=shocks[si]; if(t>=ss-1000&&t<ss){pre[si]+=H;npre[si]++;} if(t>=ss&&t<ss+1000){p1[si]+=H;np1[si]++;} if(t>=ss+4000&&t<ss+5000){p5[si]+=H;np5[si]++;}}
        double r=urand(rng),cum=0;int y=N-1;for(int j=0;j<N;j++){cum+=p[j];if(r<=cum){y=j;break;}}
        int bad=!allowed[x][y];badAll+=bad;if(t>=T-q){badLate+=bad;counts[y]++;}
        double gn=0;for(int z=0;z<D;z++){gv[z]=phi[x][y][z]+1.2*M[x][z];gn+=gv[z]*gv[z];}gn=sqrt(gn)+1e-12;for(int z=0;z<D;z++)gv[z]/=gn;
        double mu=0;for(int k=0;k<N;k++){double v=0;for(int z=0;z<D;z++)v+=phi[y][k][z]*gv[z];scores[k]=v;mu+=v;}mu/=N;
        double pn=0;for(int k=0;k<N;k++){prop[k]=0.18*(scores[k]-mu);if(mode==2 && !allowed[y][k])prop[k]=0;pn+=prop[k]*prop[k];}pn=sqrt(pn)+1e-12;
        if(mode==2){double a=min(1.0,0.12/pn);for(int i=0;i<N;i++)for(int j=0;j<N;j++)G[i][j]*=0.98;for(double &v:prop)v*=a;}
        else {for(int i=0;i<N;i++)for(int j=0;j<N;j++)G[i][j]*=0.9995;}
        double rowmu=0;for(int k=0;k<N;k++){G[y][k]+=prop[k];rowmu+=G[y][k];}rowmu/=N;for(int k=0;k<N;k++)G[y][k]-=rowmu;
        double mn=0;for(int z=0;z<D;z++){M[y][z]=0.65*M[y][z]+0.35*gv[z];mn+=M[y][z]*M[y][z];}mn=sqrt(mn);if(mn>1)for(int z=0;z<D;z++)M[y][z]/=mn;
        x=y;
    }
    int cov=0,mxcount=0;for(int c:counts){if(c>0)cov++;mxcount=max(mxcount,c);} double gn=0;for(auto &r:G)for(double v:r)gn+=v*v;gn=sqrt(gn);
    double hp=0,h1=0,h5=0;for(int i=0;i<3;i++){hp+=pre[i]/max(1,npre[i]);h1+=p1[i]/max(1,np1[i]);h5+=p5[i]/max(1,np5[i]);}hp/=3;h1/=3;h5/=3;
    return {(double)badAll/T,(double)badLate/q,HE/q,HL/q,(double)cov/N,(double)mxcount/q,gn,hp,h1,h5};
}
int main(){
    cout.setf(ios::fixed);cout<<setprecision(6);
    string labs[3]={"free","support_only","rtg"};
    vector<string> names={"bad_all","bad_late","H_early","H_late","coverage","maxshare","Gnorm","Hpre","Hpost1","Hpost5"};
    cout<<"TEN_SEED_100K\n";
    for(int m=0;m<3;m++){
        double a[10]={0};vector<Res> rs;for(int s=0;s<10;s++)rs.push_back(sim(s,100000,m));
        for(auto &r:rs){double v[10]={r.bad_all,r.bad_late,r.H_early,r.H_late,r.coverage,r.maxshare,r.Gnorm,r.Hpre,r.Hpost1,r.Hpost5};for(int i=0;i<10;i++)a[i]+=v[i]/10.0;}
        cout<<labs[m];for(int i=0;i<10;i++)cout<<" "<<names[i]<<"="<<a[i];cout<<"\n";
    }
    cout<<"ONE_SEED_1M\n";
    for(int m=0;m<3;m++){Res r=sim(101,1000000,m);double v[10]={r.bad_all,r.bad_late,r.H_early,r.H_late,r.coverage,r.maxshare,r.Gnorm,r.Hpre,r.Hpost1,r.Hpost5};cout<<labs[m];for(int i=0;i<10;i++)cout<<" "<<names[i]<<"="<<v[i];cout<<"\n";}
}
