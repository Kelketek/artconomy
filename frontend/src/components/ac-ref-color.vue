<template>
  <div class="col-6 color-reference">
    <div class="row">
      <div class="col-3 text-right">
        {{refColor.note}}
        <span v-if="editing">&nbsp;
          <ac-action :url="url" :success="callback" method="DELETE" variant="danger">
            <i class="fa fa-trash-o"></i>
          </ac-action>
        </span>
      </div>
      <div class="col-6">
        <div class="swatch text-center" :style="swatchStyle"><div class="ref-container">{{refColor.color}}</div></div>
      </div>
    </div>
  </div>
</template>
<style scoped lang="scss">
  @import '../custom-bootstrap';
  .ref-container{
    opacity: 0;
    padding: .1rem;
    display: inline-block;
  }
  .swatch {
    width: 100%;
    border: 2px solid $dark-gray;
  }
  .swatch:hover .ref-container{
    background-color: $dark-beige;
    color: $dark-purple;
    opacity: 1;
  }
</style>
<script>
  import AcAction from './ac-action'

  export default {
    components: {AcAction},
    props: ['refColor', 'editing', 'url', 'callback'],
    computed: {
      swatchStyle () {
        return (
          `background-color: ${this.refColor.color};` +
          `color: ${this.refColor.color};`
        )
      }
    }
  }
</script>