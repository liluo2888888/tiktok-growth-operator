# Scene 8: Multi-Product Comment Mining and Persona Report

## Use When

- the user wants category-level user insight from multiple best-selling products

## Minimum Inputs

- comments from at least 2 products

## Ideal Inputs

- 3-5 products
- 20-40 comments each
- market
- product positioning goal

## Workflow

1. separate comments by product
2. identify repeated praise and repeated pain
3. merge repeated signals across products
4. extract category-level persona and language
5. output product and content implications

## Output Contract

- user pain-point synthesis
- user desire synthesis
- high-frequency phrases
- persona summary
- selection and content implications

## Direct Prompt

```text
请把这些竞品评论做成一份“品类用户画像报告”。

要求：
1. 找出用户最常提到的痛点
2. 找出用户真正买单的理由
3. 找出未被满足但高频出现的需求
4. 总结出这个品类的人群画像和说话方式
5. 告诉我选品和脚本应该往哪边靠
```

## Fallback

If comment volume is low, state that the result is provisional and list what more to collect.
