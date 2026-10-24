SSDBImpl::~SSDBImpl(){
 if(binlogs){
  delete binlogs;
 }
 if(ldb){
  delete ldb;
 }
 if(options.block_cache){
  delete options.block_cache;
 }
 if(options.filter_policy){
  delete options.filter_policy;
 }
}