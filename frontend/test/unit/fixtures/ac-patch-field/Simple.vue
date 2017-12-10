<template>
  <ac-patchfield v-model="value" :multiline="multiline" :name="name" :styleclass="doStyle && style" :editmode="editing" :callback="callback && callbackMethod" :url="url"></ac-patchfield>
</template>

<script>
  import AcPatchfield from '../../../../src/components/ac-patchfield'
  import sinon from 'sinon'
  export default {
    components: {AcPatchfield},
    props: ['multiline', 'value', 'editing'],
    data: function () {
      return {
        callback: false,
        callbackMethod: sinon.spy(),
        style: 'testStyle',
        doStyle: false,
        url: '/url/to/patch/'
      }
    }
  }
</script>